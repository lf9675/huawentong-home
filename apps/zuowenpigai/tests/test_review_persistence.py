import json
import ast
from pathlib import Path
import unittest
from types import SimpleNamespace, ModuleType
from unittest.mock import MagicMock,patch

# The legacy module initializes the production DB at import time. Compile the
# actual persistence functions without invoking that unrelated startup hook.
database = ModuleType('annotation_persistence_under_test')
database.json = json
database.st = SimpleNamespace(session_state={})
database.get_conn = MagicMock()
source = ast.parse((Path(__file__).resolve().parents[1] / 'database.py').read_text())
functions = [node for node in source.body if isinstance(node, ast.FunctionDef)
             and node.name in {'save_annotation_overrides', 'save_language_audit'}]
exec(compile(ast.Module(body=functions, type_ignores=[]), 'database.py', 'exec'), database.__dict__)

class PersistenceTests(unittest.TestCase):
    def test_teacher_save_preserves_grade_and_scopes_owner(self):
        cursor=MagicMock();cursor.__enter__.return_value=cursor
        cursor.fetchone.return_value=[json.dumps({'scores':{'total':42},'other':'retain'})]
        connection=MagicMock();connection.cursor.return_value=cursor
        with patch.object(database,'st',SimpleNamespace(session_state={'annotation_teacher_auth':True})),patch.object(database,'get_conn',return_value=connection):
            database.save_annotation_overrides(5,'AC1',{'items':[]})
        args=cursor.execute.call_args_list
        self.assertEqual(args[0].args[1],(5,'AC1'))
        self.assertIn('FOR UPDATE',args[0].args[0])
        stored=json.loads(args[1].args[1][0])
        self.assertEqual(stored['scores']['total'],42);self.assertEqual(stored['other'],'retain')
        connection.commit.assert_called_once();connection.close.assert_called_once()

    def test_student_cannot_save_teacher_annotation(self):
        with patch.object(database,'st',SimpleNamespace(session_state={})),patch.object(database,'get_conn') as connect:
            with self.assertRaises(PermissionError):database.save_annotation_overrides(5,'AC1',{})
            connect.assert_not_called()

    def test_language_retry_cannot_write_other_owner(self):
        with patch.object(database,'st',SimpleNamespace(session_state={'student_id':'AC1'})),patch.object(database,'get_conn') as connect:
            with self.assertRaises(PermissionError):database.save_language_audit(5,'AC2',{})
            connect.assert_not_called()

    def test_missing_submission_closes_transaction(self):
        cursor=MagicMock();cursor.__enter__.return_value=cursor;cursor.fetchone.return_value=None
        connection=MagicMock();connection.cursor.return_value=cursor
        with patch.object(database,'st',SimpleNamespace(session_state={'annotation_teacher_auth':True})),patch.object(database,'get_conn',return_value=connection):
            with self.assertRaises(ValueError):database.save_annotation_overrides(5,'AC1',{})
        connection.commit.assert_not_called();connection.close.assert_called_once()

if __name__=='__main__':unittest.main()
