# **Real Debrid Upload (& Parser) to Telegram**



### ***A code for telegram bot do one of two things:***

- Send the direct link on a message **(Use main.py)**

  - <img src="https://i.ibb.co/RThkmPV/bixfy.jpg" alt="direct link on a message" style="zoom:50%;" />

- Download and upload the file to telegram **(Use uploader.py)**

  - <img src="https://i.ibb.co/YLkg0Cf/bixfy.jpg" alt="upload the file to telegram" style="zoom:50%;" />

  ​	

#### But wait... there is more!

*Search for* 

```python
def get_premium_link(url):
```

And add the mirror of hostings that aren't supported by Real Debird.

Example: Turbobit.net **is** supported but **not** its mirrors on Real Debrid.

('turbobif.com', 'turbobit.com', 'turb.to', 'turb.pw', 'turb.cc', 'turbo.to', 'turbo.pw', 'turbo.cc', 'turbobit.net', 'trbbt.net ')

As you can see in the code:

```python
for mirror_host in ['turbobif.com', 'turbobit.com', 'turb.to', 'turb.pw', 'turb.cc', 'turbo.to', 'turbo.pw', 'turbo.cc', 'turbobit.net', 'trbbt.net']:
    url = url.replace(mirror_host, 'turbobit.net')
```

This allows to allow the mirrors of Turbobit to be accepted. You can add more

Just do in a new line after that:

```python
for mirror_host in ['MIRROR LINK', 'MIRROR LINK']:
    url = url.replace(mirror_host, 'ACCEPTED LINK BY RD')
```



**HOWEVER....**

There is no progress bar yet. So try to check logs if anything wrong happened. 

And probably you need more requirements ><



**Thanks**

To [Oihalitz](https://github.com/Oihalitz/RealDebridTelegram) for the base code and to [Anasty17](https://github.com/anasty17) for inspiring me.



##### **StarMade ✨**
