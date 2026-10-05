# Security

## Reporting a problem

Please report a security problem privately, through
[GitHub's private reporting](https://github.com/2c2t-dev/flatpak/security/advisories/new),
rather than in a public issue: in this repository, or in an app it
serves, which is then passed on to that app's own repository. You will get
an answer, and credit if you want it, once it is fixed.

## The signing key

Every app and the repository's summary are signed with the key
`F6663D8D8E337D5BDD87A58E259BF393350BE25C`, which the `.flatpakrepo` and
`.flatpakref` files carry and which Flatpak checks every download against.
If it were ever exposed, it would be revoked, the repository signed with
a new one, and the change announced on [flatpak.2c2t.dev](https://flatpak.2c2t.dev/)
with the way to take the new key; until then, a download Flatpak cannot
verify against the key you added is refused.
