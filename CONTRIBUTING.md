# Guidance on how to contribute

> By submitting a pull request or filing a bug, issue, or feature request,
> you are agreeing to comply with this waiver of copyright interest.
> Details can be found in our [LICENSE](LICENSE).


There are two primary ways to help:
 - Using the issue tracker, and
 - Changing the code-base.


## Using the issue tracker

Use the issue tracker to suggest feature requests, report bugs, and ask questions.
This is also a great way to connect with the developers of the project as well
as others who are interested in this solution.

Use the issue tracker to find ways to contribute. Find a bug or a feature, mention in
the issue that you will take on that effort, then follow the _Changing the code-base_
guidance below.


## Changing the code-base

Generally speaking, you should fork this repository, make changes in your
own fork, and then submit a pull request. All new code should have associated
unit tests that validate implemented features and the presence or lack of defects.
Additionally, the code should follow any stylistic and architectural guidelines
prescribed by the project. In the absence of such guidelines, mimic the styles
and patterns in the existing code-base.

### Contribution guidelines
 - Your code should follow PEP 8 -- Style Guide for Python Code
 - Your changes should be covered by unit-tests

## Setup local tests (venv)

After forking the repository you may create a `venv` to manage all dependencies required for running the tests:
```
python -m virtualenv venv
```

You can than enter the newly created `venv` and install all dependencies required for the tests:
```
user@computer: source venv/bin/activate
(venv) user@computer: pip install -r requirements.txt
(venv) user@computer: pip install -e .
```

A quick check via `pip freeze` should list all relevant dependency packages plus the `django-attachments`:
```
(venv) user@computer: pip freeze
Django==2.2.24
# Editable Git install with no remote (django-attachments==0.0.0)
-e /media/alex/INTENSO/ANX/pycharmWorkspace/django-attachments
python-magic==0.4.24
pytz==2021.3
sqlparse==0.4.2
```

Now you should be able to successfully run the tests provided in `/tests/`:
```
(venv) user@computer: python tests/manage.py test test tests/test/
```