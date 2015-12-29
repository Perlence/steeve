Steeve Changelog
================

Version 0.2
-----------

Second release, December 30th, 2015.

- Set target's default to parent of stow dir.
- Remove ``current`` link when stow failed.
- Abort when trying to unstow nonstowed package or uninstall missing package.
- Join commands ``install`` and ``reinstall``,  ``stow`` and ``restow``.
- Uninstall requires user prompt.
- Check if path exists before installing.
- Add tests.

Version 0.1.1
-------------

Bugfix release, December 24th, 2015.

- Check if GNU Stow is installed before attempting anything.
- Ignore output to ``stderr`` in fish completion.

Version 0.1
-----------

First public release, September 2nd, 2015.

- Initial release.
