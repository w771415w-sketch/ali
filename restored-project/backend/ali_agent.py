# -*- coding: utf-8 -*-
"""Compatibility entry point for older ALI Agent integrations/tests.

The canonical desktop application lives in ``ali_ai.py``. This adapter preserves
small legacy helper methods while delegating real work to the new runtime.
"""
from ali_ai import App as _App, main, load_cfg, save_cfg, ROOT, DB, C
from config.paths import APP_PATHS
import tkinter as tk

class App(_App):
    def __init__(self, root):
        super().__init__(root)
        self.perm_mode = tk.StringVar(value=self.runtime.permission_manager.mode)
        self.perm_mode.trace_add('write', self._sync_perm_mode)

    def _sync_perm_mode(self, *_):
        mode=self.perm_mode.get()
        if mode:
            self.runtime.permission_manager.set_mode(mode)
            self.cfg['perm_mode']=mode
            save_cfg(self.cfg)

    def _dispatch_tool(self, text):
        t=text.strip(); low=t.lower()
        if low.startswith(('read_file ','read ')):
            return ('read_file', {'path': t.split(None,1)[1]}, None)
        if low in ('list_dir','ls') or low.startswith(('list_dir ','ls ')):
            return ('list_dir', {'path': t.split(None,1)[1] if len(t.split(None,1))>1 else ''}, None)
        if low.startswith(('search_files ','search ')):
            return ('search_files', {'pattern': t.split(None,1)[1]}, None)
        if low.startswith(('write_file ','write ')):
            return ('write_file', {'path': t.split(None,1)[1]}, None)
        if low.startswith(('run_command ','run ')):
            return ('run_command', {'command': t.split(None,1)[1]}, None)
        if low.startswith('git status'):
            return ('git_status', {}, None)
        if low.startswith('git diff'):
            return ('git_diff', {}, None)
        return None

    def _local_reply(self, text):
        d=self._dispatch_tool(text)
        if d:
            name,kwargs,_=d
            ctx=self._compat_context()
            result=self.runtime._tool(name,ctx,**kwargs)
            if result.get('ok'):
                try:
                    from database.database import get_db, ToolCallRepo
                    repo=ToolCallRepo(get_db()); call_id=repo.start(None,None,name,kwargs); repo.finish(call_id,'completed',result.get('data'))
                except Exception:
                    pass
                return f"✅ نجح تنفيذ {name}\n{result.get('data','')}"
            return f"⚠ فشل تنفيذ {name}: {result.get('error','unknown error')}"
        names=', '.join(sorted(self.runtime.registry.all()))
        return names

    def _compat_context(self):
        from core.context import ConversationContext
        return ConversationContext('compat',self.project_dir,self.runtime.permission_manager.mode,'ALI','high',tool_registry=self.runtime.registry)

__all__=["App","main","load_cfg","save_cfg","ROOT","DB","C","APP_PATHS"]

if __name__ == "__main__":
    main()
