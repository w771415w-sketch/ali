from memory.sessions import ConversationSessionStore

def test_conversation_sessions_roundtrip(tmp_path):
    s=ConversationSessionStore(tmp_path/'sessions.sqlite3')
    row=s.create('محادثة جديدة','v1')
    sid=row['id']
    s.append(sid,'user','مرحبا','v1')
    s.append(sid,'assistant','أهلاً بك','v1')
    got=s.get(sid)
    assert got['title'].startswith('مرحبا')
    assert [m['role'] for m in got['messages']] == ['user','assistant']
    s.rename(sid,'مشروعي')
    assert s.get(sid)['title'].startswith('مشروعي')
    assert s.delete(sid) is True
    assert s.list() == []
