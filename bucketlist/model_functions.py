from bucketlist.extensions import db
from bucketlist.models import User, Bucketlistitem, Bucketlist


def create_user(data):
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    user = User(username, email, password)
    db.session.add(user)
    db.session.commit()


def update_user(user_id, data):
    user = User.query.filter_by(id=user_id)
    user.name = data.get('name')
    user.username = data.get('username')
    user.password = data.get('password')
    db.session.add(user)
    db.session.commit()


def delete_user(user_id):
    user = User.query.filter_by(id=user_id).one()
    db.session.delete(user)
    db.session.commit()


def create_bucketlist(user_id, data):
    try:
        name = data.get('name')
    except AttributeError:
        return None, 404
    bucketlist = Bucketlist(name, user_id)
    db.session.add(bucketlist)
    db.session.commit()


def update_bucketlist(bucketlist_id, user_id,  data):
    bucketlist = Bucketlist.query.filter_by(id=bucketlist_id).first()
    if not bucketlist:
        return None, 404
    bucketlist.name = data.get('name')
    bucketlist.user_id = user_id
    db.session.add(bucketlist)
    db.session.commit()


def delete_bucketlist(bucketlist_id):
    bucketlist = Bucketlist.query.filter_by(id=bucketlist_id).first()
    if not bucketlist:
        return None, 404
    db.session.delete(bucketlist)
    db.session.commit()


def create_bucketlistitem(bucketlist_id, data):
    name = data.get('name')
    done = data.get('done')
    bucketlist_id = bucketlist_id
    bucketlistitem = Bucketlistitem(name, done, bucketlist_id )
    db.session.add(bucketlistitem)
    db.session.commit()


def update_bucketlistitem(bucketlistitem_id, bucketlist_id, data):
    bucketlistitem = Bucketlistitem.query.filter_by(id=bucketlistitem_id, bucketlist_id=bucketlist_id).one()
    bucketlistitem.name = data.get('name')
    bucketlistitem.done = data.get('done')
    bucketlistitem.bucketlist_id = bucketlist_id
    db.session.add(bucketlistitem)
    db.session.commit()


def delete_bucketlistitem(bucketlistitem_id, bucketlist_id):
    bucketlistitem = Bucketlistitem.query.filter_by(id=bucketlistitem_id, bucketlist_id=bucketlist_id).one()
    db.session.delete(bucketlistitem)
    db.session.commit()