from ...objects import dp, MySignalEvent
from ...utils import new_message, edit_message, user_f
from ...lpcommands.utils import find_user_mention

def tr_user_op(event, error, typ):
    tr_id = find_user_mention(event.msg['text'])

    if event.reply_message == None:
        edit_message(event.api, event.chat.peer_id, event.msg['id'],
        message = event.responses['trusted_err_no_reply'])
        return "ok"

    def tr_err():
        edit_message(event.api, event.chat.peer_id, event.msg['id'], 
        message = event.responses[f'trusted_err_{error}'])
        return "ok"

    tr_id = event.reply_message['from_id'] if event.reply_message else tr_id
    if typ == 'add':
        if tr_id in event.db.trusted_users: return tr_err()
    else:
        if tr_id not in event.db.trusted_users: return tr_err()
            
    tr_user = event.api('users.get', user_ids=tr_id)[0]
    
    if typ == 'add':
        event.db.trusted_users.append(tr_id)
        event.db.save()
    else:
        event.db.trusted_users.remove(tr_id)
        event.db.save()

    edit_message(event.api, event.chat.peer_id, event.msg['id'], 
        message= event.responses[f'trusted_success_{typ}'].format(
        ссылка = user_f(tr_user)))
    return "ok"

@dp.my_signal_event_register('+дов')
def add_trusted_user(event: MySignalEvent) -> str:
    return tr_user_op(event, 'in_tr', 'add')


@dp.my_signal_event_register('-дов')
def remove_trusted_user(event: MySignalEvent) -> str:
    return tr_user_op(event, 'not_in_tr', 'rem')


@dp.my_signal_event_register('доверенные', "довы")
def trusted_users(event: MySignalEvent) -> str:
    users = event.api('users.get', user_ids=",".join([str(i) for i in event.db.trusted_users]))

    message = event.responses['trusted_list']
    itr = 0
    for user in users:
        itr += 1
        message += f"\n{itr}. [id{user['id']}|{user['first_name']} {user['last_name']}]"
    
    edit_message(event.api, event.chat.peer_id, event.msg['id'], message=message)

    return "ok"