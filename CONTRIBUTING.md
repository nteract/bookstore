# Contributing

Oh, hello there! You're probably reading this because you are interested in
contributing to nteract. That's great to hear! This document will help you
through your journey of open source. Love it, cherish it, take it out to
dinner, but most importantly: read it thoroughly!

## What do I need to know to help?

Read the README.md file. This will help you set up the project. If you have
questions, please ask on the nteract Slack channel. We're a welcoming project and
are happy to answer your questions.

## How do I make a contribution?

Never made an open source contribution before? Wondering how contributions work
in the nteract world? Here's a quick rundown!

1. Find an issue that you are interested in addressing or a feature that you
   would like to address.
2. Fork the repository associated with the issue to your local GitHub
   organization.
3. Clone the repository to your local machine using:

       git clone https://github.com/github-username/repository-name.git

4. Create a new branch for your fix using:

       git checkout -b branch-name-here

5. Make the appropriate changes for the issue you are trying to address or the
   feature that you want to add.
6. You can run python unit tests using `pytest`. Running integration tests
   locally requires a more complicated setup. This setup is described in
   [running_ci_locally.md](./running_ci_locally.md)
7. Add and commit the changed files using `git add` and `git commit`.
8. Push the changes to the remote repository using:

       git push origin branch-name-here

9. Submit a pull request to the upstream repository.
10. Title the pull request per the requirements outlined in the section below.
11. Set the description of the pull request with a brief description of what you
    did and any questions you might have about what you did.
12. Wait for the pull request to be reviewed by a maintainer.
13. Make changes to the pull request if the reviewing maintainer recommends
    them.
14. Celebrate your success after your pull request is merged! :tada:

## How should I write my commit messages and PR titles?

Good commit messages serve at least three important purposes:

* To speed up the reviewing process.

* To help us write a good release note.

* To help the future maintainers of nteract/nteract (it could be you!), say
  five years into the future, to find out why a particular change was made to
  the code or why a specific feature was added.

Structure your commit message like this:

```text
> Short (50 chars or less) summary of changes
>
> More detailed explanatory text, if necessary.  Wrap it to about 72
> characters or so.  In some contexts, the first line is treated as the
> subject of an email and the rest of the text as the body.  The blank
> line separating the summary from the body is critical (unless you omit
> the body entirely); tools like rebase can get confused if you run the
> two together.
>
> Further paragraphs come after blank lines.
>
>   - Bullet points are okay, too
>
>   - Typically a hyphen or asterisk is used for the bullet, preceded by a
>     single space, with blank lines in between, but conventions vary here
>
```

*Source:* https://git-scm.com/book/ch5-2.html

### DO

* Write the summary line and description of what you have done in the
  imperative mode, that is as if you were commanding. Start the line
  with "Fix", "Add", "Change" instead of "Fixed", "Added", "Changed".
* Always leave the second line blank.
* Line break the commit message (to make the commit message readable
  without having to scroll horizontally in gitk).

### DON'T

* Don't end the summary line with a period - it's a title and titles don't end
  with a period.

### Tips

* If it seems difficult to summarize what your commit does, it may be because it
  includes several logical changes or bug fixes, and are better split up into
  several commits using `git add -p`.

### References

The following blog post has a nice discussion of commit messages:

* "On commit messages" http://who-t.blogspot.com/2009/12/on-commit-messages.html

## How fast will my PR be merged?

Your pull request will be merged as soon as there are maintainers to review it
and after tests have passed. You might have to make some changes before your
PR is merged but as long as you adhere to the steps above and try your best,
you should have no problem getting your PR merged.

That's it! You're good to go!
