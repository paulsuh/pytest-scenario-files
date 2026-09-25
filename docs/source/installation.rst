##############
 Installation
##############

This plug-in can be installed from PyPI using ``pip``, with the command:

.. code-block::

    pip install pytest-scenario-files

That's all! No additional settings or flags, no need to add import statements or
decorators to your tests.

If you want to utilize the Responses integration you can either install the Responses
package separately or specify the Responses extra:

.. code-block::

    pip install pytest-scenario-files[responses]

Similarly, if you want to utilize the Respx integration you can either install the Respx
package directly or you can specify the Respx extra:

.. code-block::

    pip install pytest-scenario-files[respx]

Claude Code Skill
------------------

If you use `Claude Code <https://claude.com/product/claude-code>`_, this package
ships with a skill that teaches Claude how to use pytest-scenario-files effectively
in your project — when a data file is worth it, where to put it, and the plugin's
sharper edges. It's entirely optional and does nothing unless installed. After
installing the package, run:

.. code-block::

    pytest-scenario-files-install-skill

This copies the skill into ``~/.claude/skills/pytest-scenario-files``, where Claude
Code will pick it up automatically. Re-run the command (with ``--force`` if you have
local edits to overwrite) after upgrading the package to pick up skill updates.

