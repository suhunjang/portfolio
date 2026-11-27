"""tdd-guard.py 회귀 테스트 (HOO-124 Astra blocker 4·5).

실행: python3 -m unittest scripts/hooks/test_tdd_guard.py
합성 git 저장소를 임시 폴더에 만들고 실제 hook 프로세스를 호출한다.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tdd-guard.py")
KO_SPEC = "tests/specs/대표카드.spec.js"


def git(repo, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    subprocess.run(["git", "-C", repo] + list(args), check=True, capture_output=True, env=env)


class TddGuardTest(unittest.TestCase):
    def setUp(self):
        self.repo = os.path.realpath(tempfile.mkdtemp(prefix="tdd-guard-test-"))
        os.makedirs(os.path.join(self.repo, "js"))
        os.makedirs(os.path.join(self.repo, "tests", "specs"))
        with open(os.path.join(self.repo, "tdd.json"), "w") as f:
            json.dump({"implGlobs": ["index.html", "css/**", "js/**"],
                       "testGlobs": ["tests/specs/**"], "baseRef": "base"}, f)
        self.write("js/main.js", "// v1\n")
        self.write("tests/specs/a.spec.js", "// a\n")
        git(self.repo, "init", "-q")
        git(self.repo, "add", "-A")
        self.commit("base")
        git(self.repo, "tag", "base")

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def write(self, rel, text):
        p = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)

    def commit(self, msg):
        git(self.repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", msg)

    def run_hook(self, payload):
        raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.repo)
        r = subprocess.run([sys.executable, HOOK], input=raw, capture_output=True, text=True, env=env)
        return r.returncode

    def edit(self, rel="js/main.js"):
        return {"tool_name": "Edit", "tool_input": {"file_path": os.path.join(self.repo, rel)}}

    # 기존 계약 (회귀 방지)
    def test_impl_without_test_change_is_denied(self):
        self.assertEqual(self.run_hook(self.edit()), 2)

    def test_impl_after_ascii_test_change_is_allowed(self):
        self.write("tests/specs/a.spec.js", "// a2\n")
        self.assertEqual(self.run_hook(self.edit()), 0)

    def test_test_file_edit_is_allowed(self):
        self.assertEqual(self.run_hook(self.edit("tests/specs/a.spec.js")), 0)

    def test_broken_json_is_denied(self):
        self.assertEqual(self.run_hook("not json"), 2)

    # blocker 4: dict가 아닌 입력은 exit 1이 아니라 exit 2(차단)
    def test_tool_input_string_is_denied(self):
        self.assertEqual(self.run_hook({"tool_name": "Edit", "tool_input": "x"}), 2)

    def test_tool_input_list_is_denied(self):
        self.assertEqual(self.run_hook({"tool_name": "Edit", "tool_input": ["a"]}), 2)

    def test_edits_not_list_is_denied(self):
        self.assertEqual(self.run_hook({"tool_name": "MultiEdit", "tool_input": {"edits": 5}}), 2)

    def test_tool_name_not_string_is_denied(self):
        self.assertEqual(self.run_hook({"tool_name": 5, "tool_input": {"file_path": "README.md"}}), 2)

    # closure1: null·누락·배열 원소 형태 오류도 exit 2
    def test_tool_input_null_is_denied(self):
        self.assertEqual(self.run_hook({"tool_name": "Edit", "tool_input": None}), 2)

    def test_tool_input_missing_is_denied(self):
        self.assertEqual(self.run_hook({"tool_name": "Edit"}), 2)

    # 문서 경로(정상이면 허용)를 써서, 차단이 입력 형식 검사 때문인지 확인한다
    def test_tool_name_null_is_denied(self):
        self.assertEqual(self.run_hook({"tool_name": None, "tool_input": {"file_path": "README.md"}}), 2)

    def test_tool_name_missing_is_denied(self):
        self.assertEqual(self.run_hook({"tool_input": {"file_path": "README.md"}}), 2)

    def test_edits_null_is_denied(self):
        self.assertEqual(self.run_hook({"tool_name": "MultiEdit", "tool_input": {"edits": None}}), 2)

    def test_edits_item_not_object_is_denied(self):
        self.assertEqual(self.run_hook({"tool_name": "MultiEdit", "tool_input": {"edits": [5]}}), 2)

    def test_multiedit_normal_shape_still_checked(self):
        payload = {"tool_name": "MultiEdit", "tool_input": {
            "file_path": os.path.join(self.repo, "js/main.js"),
            "edits": [{"old_string": "v1", "new_string": "v2"}]}}
        self.assertEqual(self.run_hook(payload), 2)
        self.write("tests/specs/a.spec.js", "// a2\n")
        self.assertEqual(self.run_hook(payload), 0)

    # blocker 5: 한글 이름 테스트 파일 변경을 인식
    def test_untracked_korean_test_allows_impl(self):
        self.write(KO_SPEC, "// ko\n")
        self.assertEqual(self.run_hook(self.edit()), 0)

    def test_modified_korean_test_allows_impl(self):
        self.write(KO_SPEC, "// ko\n")
        git(self.repo, "add", "-A")
        self.commit("add ko spec")
        git(self.repo, "tag", "-f", "base")
        self.write(KO_SPEC, "// ko2\n")
        self.assertEqual(self.run_hook(self.edit()), 0)

    def test_committed_korean_test_after_impl_allows_impl(self):
        self.write("js/main.js", "// v2\n")
        git(self.repo, "add", "-A")
        self.commit("impl")
        self.write(KO_SPEC, "// ko\n")
        git(self.repo, "add", "-A")
        self.commit("test ko")
        self.assertEqual(self.run_hook(self.edit()), 0)

    def test_committed_test_before_latest_impl_is_denied(self):
        self.write(KO_SPEC, "// ko\n")
        git(self.repo, "add", "-A")
        self.commit("test ko")
        self.write("js/main.js", "// v2\n")
        git(self.repo, "add", "-A")
        self.commit("impl")
        self.assertEqual(self.run_hook(self.edit()), 2)


if __name__ == "__main__":
    unittest.main()
