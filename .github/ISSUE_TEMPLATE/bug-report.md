---
name: Bug Report
about: Report an error or problem

---

## Please follow the guide below

- Issues submitted without this template format will be **ignored**.
- Please read the questions **carefully** and answer completely.
- Do not post screenshots of error messages or code.
- Put an `x` into all the boxes [ ] relevant to your issue (like so [x] no spaces).
- Use the *Preview* tab to see how your issue will actually look like.

---

### Before submitting an issue make sure you have:
- [ ] Updated to the lastest version v0.3.8
- [ ] Read the [README](https://github.com/ping/instagram_private_api_extensions/blob/master/README.md)
- [ ] [Searched](https://github.com/ping/instagram_private_api_extensions/search?type=Issues) the bugtracker for similar issues including **closed** ones

---

### Describe the Bug/Error:

Please make sure the description is worded well enough to be understood with as much context and examples as possible.

Code to replicate the error must be provided below.

---

Paste the output of ``python -V`` here:

Code:

```python
# Example code that will produce the error reported
from instagram_web_api import Client

web_api = Client()
user_feed_info = web_api.user_feed('1234567890', count=10)
```

Error/Debug Log:

```python
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ZeroDivisionError: integer division or modulo by zero
```
