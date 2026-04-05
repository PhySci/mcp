import json
import select
import subprocess
import sys
import unittest
from pathlib import Path
from pprint import pprint
from typing import Dict

MAX_TIMEOUT = 15.0


class TestMCP(unittest.TestCase):
    _mcp_proc: subprocess.Popen[str] | None = None

    @classmethod
    def setUpClass(cls):
        main_py = Path(__file__).resolve().parent.parent / "main.py"
        cls._mcp_proc = subprocess.Popen(
            [sys.executable, str(main_py), "-t", "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )

    @classmethod
    def tearDownClass(cls):
        if cls._mcp_proc is None:
            return
        proc = cls._mcp_proc
        cls._mcp_proc = None
        for stream in (proc.stdin, proc.stdout):
            if stream is not None:
                try:
                    stream.close()
                except OSError:
                    pass
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

    def _read_write(self, request: Dict) -> Dict:
        proc = type(self)._mcp_proc
        if proc is None:
            self.fail("MCP subprocess was not started in setUpClass")

        assert proc.stdin is not None
        proc.stdin.write(json.dumps(request) + "\n")
        proc.stdin.flush()

        if proc.stdout is None:
            raise RuntimeError("stdout is not a pipe")
        ready, _, _ = select.select([proc.stdout], [], [], MAX_TIMEOUT)
        if not ready:
            raise TimeoutError("timed out waiting for MCP response on stdout")
        line = proc.stdout.readline()
        if not line:
            raise EOFError("unexpected EOF from MCP stdout")

        data = json.loads(line)
        pprint(data)
        return data

    def test_1_initialize(self):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"elicitation": {}},
                "clientInfo": {
                    "name": "example-client",
                    "version": "1.0.0",
                },
            },
        }

        data = self._read_write(request)

        self.assertEqual(data.get("jsonrpc"), "2.0")
        self.assertEqual(data.get("id"), 1)
        self.assertIn("result", data)
        result = data["result"]
        self.assertEqual(result["protocolVersion"], "2025-06-18")
        self.assertEqual(result["serverInfo"]["name"], "postgres_mcp")

    def test_2_tool_list(self):
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            }

        data = self._read_write(request)
        tools = data.get("result", {}).get("tools", [])
        self.assertGreater(len(tools), 0)

    def test_3_get_tables(self):
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_all_tables",
                "arguments": {}

            }
        }

        data = self._read_write(request)

        try:
            result = data["result"]["structuredContent"]["result"]
            self.assertGreater(len(result), 0)
        except:
            self.fail("Result is incomplete")



if __name__ == "__main__":
    unittest.main()
