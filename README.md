# 2c2t Flatpak

The Flatpak repository of 2c2t's Linux apps, served at
[flatpak.2c2t.dev](https://flatpak.2c2t.dev/). The apps update with the rest
of your Flatpaks, and run on Flathub's runtimes.

## Adding it

```sh
flatpak remote-add --if-not-exists 2c2t https://flatpak.2c2t.dev/2c2t.flatpakrepo
```

Then install an app with `flatpak install 2c2t <id>`, or from GNOME
Software or Discover, which list the repository's apps once it is added.

| App | Id |
| --- | --- |
| [Pipedeck](https://pipedeck.2c2t.dev/), the PipeWire mixer for Linux streamers | `dev._2c2t.Pipedeck` |

Everything in it is signed with the key
`F6663D8D8E337D5BDD87A58E259BF393350BE25C`.

## How it is made

Each app builds its own Flatpak and puts the bundle on its releases. Every
hour, the *Publish* workflow here looks at each app's latest release, and
when one is new, imports the bundles into one repository, signs it, and
publishes it on Cloudflare Pages with the page `build.py` makes from
`apps.json`. Started by hand, or by a change here, it publishes at once.

To add an app, give it an entry in `apps.json`: its id, name, summary,
GitHub repository, website and icon. Its releases must carry a `.flatpak`
bundle built on the `stable` branch.
