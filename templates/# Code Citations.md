# Code Citations

## License: unknown
https://github.com/prrrffrrrp/december-blog/blob/e9a1b16d7355cce78a42f01887403549a741b277/app/auth/views.py

```
redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
```


## License: unknown
https://github.com/ackerr/Flask-blog/blob/a841b4544d8f019e9e9fd469a16b462de1c54ff7/src/auth/views.py

```
redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
```


## License: unknown
https://github.com/hziling/Blog/blob/d1ce0ab12f449c2949f597bfdc2d81f416ccdb01/app/auth/views.py

```
redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
```


## License: unknown
https://github.com/scrapeandmake/cl-scraper/blob/230e0f597a046761d1f58f9b9dd95352e5520ed6/cl_scraper/views/users.py

```
redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
```


## License: unknown
https://github.com/caser789/xblog/blob/508b11caa2523f6d13e3a42b3e7a68c5b9b6aac8/app/auth/views.py

```
redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
```


## License: unknown
https://github.com/Ilcyb/quwaner/blob/c3e6665696a35386278e6b8bf6d55207be1f67e0/app/auth/views.py

```
redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
```


## License: unknown
https://github.com/jaapz/winkel-van-de-toekomst/blob/4b957aed846336bd86068d4fbca11dd190f51684/app/templates/users/register.html

```
>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.username.label }} {{ form.username(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.confirm_password.label }} {{ form.confirm_password(class="form-control") }}
    </div>
    <
```


## License: unknown
https://github.com/PyLadies-UHack/operation-locusts/blob/cbdbf3b2c4ef2f4dbe400085e729b94f1afe1691/app/templates/login.html

```
>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.username.label }} {{ form.username(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.confirm_password.label }} {{ form.confirm_password(class="form-control") }}
    </div>
    <
```


## License: unknown
https://github.com/bwainstock/leaflet-flask/blob/06a09f7abad34092b3cbb7b55f2dd7eae91bbfb4/app/templates/register.html

```
>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.username.label }} {{ form.username(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.confirm_password.label }} {{ form.confirm_password(class="form-control") }}
    </div>
    <
```


## License: unknown
https://github.com/bwainstock/leaflet-flask/blob/06a09f7abad34092b3cbb7b55f2dd7eae91bbfb4/app/templates/login.html

```
>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.username.label }} {{ form.username(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.confirm_password.label }} {{ form.confirm_password(class="form-control") }}
    </div>
    <
```


## License: GPL-3.0
https://github.com/opendatakosovo/open-arbk/blob/7f621ee63701119f6ae2560359fde9530ee7eb9e/app/admin/authors/templates/authors/add_author.html

```
>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.username.label }} {{ form.username(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.confirm_password.label }} {{ form.confirm_password(class="form-control") }}
    </div>
    <
```


## License: unknown
https://github.com/rittwickBhabak/Typemaster/blob/4da292e74b166f47c49c2e185ab4ec158c832acc/myproject/templates/login.html

```
>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.username.label }} {{ form.username(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.confirm_password.label }} {{ form.confirm_password(class="form-control") }}
    </div>
    <
```


## License: GPL-3.0
https://github.com/opatut/mini/blob/7a0a2d8922e9a9a22c9d0b35c33d57f494a36b1e/mini/templates/account/login.html

```
>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.username.label }} {{ form.username(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.confirm_password.label }} {{ form.confirm_password(class="form-control") }}
    </div>
    <
```


## License: GPL-3.0
https://github.com/opatut/mini/blob/7a0a2d8922e9a9a22c9d0b35c33d57f494a36b1e/mini/templates/account/register.html

```
>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.username.label }} {{ form.username(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.confirm_password.label }} {{ form.confirm_password(class="form-control") }}
    </div>
    <
```


## License: unknown
https://github.com/sirfransome/Loan-application-system/blob/f3bd9f2547921712a33b388b751fd3031b907e5a/templates/login.html

```
% extends "base.html" %}

{% block content %}
<h2>Login</h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    {{ form.submit(class="btn btn-primary") }}
<
```


## License: unknown
https://github.com/saintfortjohnb/render/blob/feef76daaef663341f81efe24904e9c63e2e7622/templates/login.html

```
% extends "base.html" %}

{% block content %}
<h2>Login</h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    {{ form.submit(class="btn btn-primary") }}
<
```


## License: unknown
https://github.com/PyLadies-UHack/operation-locusts/blob/cbdbf3b2c4ef2f4dbe400085e729b94f1afe1691/app/templates/login.html

```
% extends "base.html" %}

{% block content %}
<h2>Login</h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    {{ form.submit(class="btn btn-primary") }}
<
```


## License: unknown
https://github.com/Kaper156/olympiad_experts/blob/9c0f8e8a88a15463065ad47fc4dd2a6a3ee9a84f/app/templates/login.html

```
% extends "base.html" %}

{% block content %}
<h2>Login</h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    {{ form.submit(class="btn btn-primary") }}
<
```


## License: unknown
https://github.com/cfangmeier/BOM-Manager/blob/c598cfa5dc5129bb617d2ebf23111ec705651293/app/templates/login.html

```
% extends "base.html" %}

{% block content %}
<h2>Login</h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    {{ form.submit(class="btn btn-primary") }}
<
```


## License: GPL-3.0
https://github.com/opendatakosovo/open-arbk/blob/7f621ee63701119f6ae2560359fde9530ee7eb9e/app/admin/templates/admin/admin_login.html

```
% extends "base.html" %}

{% block content %}
<h2>Login</h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    {{ form.submit(class="btn btn-primary") }}
<
```


## License: unknown
https://github.com/MukeshDubey1420/Flask_Documentation/blob/d8a5213bde919de4cf4db937347b12fe69468abe/13.%20user_login/myproject/templates/login.html

```
% extends "base.html" %}

{% block content %}
<h2>Login</h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.email.label }} {{ form.email(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.password.label }} {{ form.password(class="form-control") }}
    </div>
    {{ form.submit(class="btn btn-primary") }}
<
```


## License: unknown
https://github.com/frad00r4/b_acc/blob/ce6fb93215c1d3f80ba6db78c040a26dad725338/b_acc/templates/b_acc/add_document.html

```
h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.name.label }} {{ form.name(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.description.label }} {{ form.description(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.price.label }} {{ form.price(class="form-control") }}
    </div
```


## License: GPL-3.0
https://github.com/honmaple/maple-bbs/blob/25a2282225b86993023b7199bcb019c1f277f66c/templates/collect/create.html

```
h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.name.label }} {{ form.name(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.description.label }} {{ form.description(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.price.label }} {{ form.price(class="form-control") }}
    </div
```


## License: unknown
https://github.com/humzahasan/Online-Bidding-Portal/blob/02daabef54049c46c54ce43e61b51c34591aa85f/templates/photo_upload.html

```
h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.name.label }} {{ form.name(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.description.label }} {{ form.description(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.price.label }} {{ form.price(class="form-control") }}
    </div
```


## License: unknown
https://github.com/0xCarti/AssetFlow/blob/0bdccbdcdad4b7a1953212d15185510c2a9f1e00/app/templates/items/add_item.html

```
h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.name.label }} {{ form.name(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.description.label }} {{ form.description(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.price.label }} {{ form.price(class="form-control") }}
    </div
```


## License: unknown
https://github.com/johnschimmel/itp-dwd-flask-s3-upload/blob/d6e433ee4cc34e91bae756b283fb2997dceaf804/templates/main.html

```
h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.name.label }} {{ form.name(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.description.label }} {{ form.description(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.price.label }} {{ form.price(class="form-control") }}
    </div
```


## License: Apache-2.0
https://github.com/christiansyoung/EIT_ORK/blob/f9e3a439734726b88d177e671de1fa414640b3ef/templates/login.html

```
h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.name.label }} {{ form.name(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.description.label }} {{ form.description(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.price.label }} {{ form.price(class="form-control") }}
    </div
```


## License: MIT
https://github.com/hreeder/WHAuth/blob/571fa76f5a83cecc28590d74b8d2524f669a6c3e/auth/admin/templates/admin/groups/add_group.html

```
h2>
<form method="POST">
    {{ form.hidden_tag() }}
    <div class="form-group">
        {{ form.name.label }} {{ form.name(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.description.label }} {{ form.description(class="form-control") }}
    </div>
    <div class="form-group">
        {{ form.price.label }} {{ form.price(class="form-control") }}
    </div
```

