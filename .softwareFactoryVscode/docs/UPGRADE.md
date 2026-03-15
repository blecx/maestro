# Upgrade

## Supported upgrade paths

- same-schema runtime metadata refreshes
- versioned upgrades that preserve host runtime state under `.tmp/softwareFactoryVscode/`

## Backup advice

Before major upgrades, commit host changes and the hidden `.softwareFactoryVscode/` tool checkout if you vendor it directly.

## Lock behavior

`.factory.lock.json` records the current factory version, projection version, install path, and last upgrade timestamp.

## Isolation guarantee

The upgrade flow does not project tool-owned `.vscode/`, `.github/`, or `.copilot/` files into the host repository.

Host-project editor and governance files remain host-owned.

## Upgrade flow

- update the nested factory checkout/submodule
- run `python3 .softwareFactoryVscode/scripts/project_upgrade.py --target . --factory-root .softwareFactoryVscode`
- rerun runtime validation

## Rollback

- switch the nested factory repo back to the previous tag/commit
- rerun `project_upgrade.py`
- revalidate the runtime
