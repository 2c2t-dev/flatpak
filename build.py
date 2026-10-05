#!/usr/bin/env python3
"""The site flatpak.2c2t.dev serves beside the repository: a page listing
the apps, the .flatpakrepo that adds the repository, a .flatpakref for each
app, and the headers Cloudflare sends with them.

    build.py versions                         the latest release of each app, as JSON
    build.py site OUT --key KEY --fingerprint FPR --versions FILE

The apps are listed in apps.json. Nothing but the standard library: the
workflow runs it as it is.
"""

import argparse
import base64
import html
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
URL = "https://flatpak.2c2t.dev"
REMOTE = "2c2t"
BRANCH = "stable"
FLATHUB = "https://dl.flathub.org/repo/flathub.flatpakrepo"


def apps() -> list[dict]:
    return json.loads((HERE / "apps.json").read_text())


def latest_release(repository: str) -> str:
    """The tag of a repository's latest release, as GitHub has it."""
    return subprocess.run(
        ["gh", "release", "view", "--repo", repository, "--json", "tagName", "--jq", ".tagName"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def flatpakrepo(key64: str) -> str:
    return (
        "[Flatpak Repo]\n"
        f"Title=2c2t\n"
        f"Url={URL}/repo/\n"
        f"Homepage={URL}/\n"
        "Comment=Linux apps by 2c2t\n"
        f"Icon={URL}/icon.svg\n"
        f"GPGKey={key64}\n"
    )


def flatpakref(app: dict, key64: str) -> str:
    return (
        "[Flatpak Ref]\n"
        f"Name={app['id']}\n"
        f"Branch={BRANCH}\n"
        f"Title={app['name']}\n"
        f"Url={URL}/repo/\n"
        f"SuggestRemoteName={REMOTE}\n"
        f"RuntimeRepo={FLATHUB}\n"
        "IsRuntime=false\n"
        f"GPGKey={key64}\n"
    )


def headers(listed: list[dict]) -> str:
    """The page loads its own files and nothing else; what adds the
    repository and what installs an app carry their own types, so a browser
    hands them to GNOME Software or Discover."""
    lines = [
        "/*",
        "  Content-Security-Policy: default-src 'none'; style-src 'self'; img-src 'self'; "
        "base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        "  X-Content-Type-Options: nosniff",
        "  Referrer-Policy: strict-origin-when-cross-origin",
        "  Strict-Transport-Security: max-age=63072000; includeSubDomains",
        "",
        "/2c2t.flatpakrepo",
        "  Content-Type: application/vnd.flatpak.repo",
    ]
    for app in listed:
        lines += ["", f"/{app['id']}.flatpakref", "  Content-Type: application/vnd.flatpak.ref"]
    return "\n".join(lines) + "\n"


def page(listed: list[dict], versions: dict, fingerprint: str) -> str:
    e = html.escape
    cards = []
    for app in listed:
        version = versions.get(app["id"], "")
        cards.append(
            f"""      <article class="app">
        <img src="icons/{e(app['id'])}.svg" width="64" height="64" alt="">
        <div class="about">
          <h3>{e(app['name'])} <span class="version">{e(version.lstrip('v'))}</span></h3>
          <p>{e(app['summary'])}</p>
          <pre><code>flatpak install {REMOTE} {e(app['id'])}</code></pre>
          <p class="links"><a class="button" href="{e(app['id'])}.flatpakref">Install</a>
            <a href="{e(app['homepage'])}">Website</a></p>
        </div>
      </article>"""
        )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>2c2t Flatpak</title>
<meta name="description" content="Linux apps by 2c2t, as Flatpaks that keep themselves up to date.">
<link rel="icon" href="icon.svg">
<link rel="stylesheet" href="style.css">
</head>
<body>
  <main>
    <header>
      <h1>2c2t Flatpak</h1>
      <p class="lead">Linux apps by 2c2t, as Flatpaks that keep themselves up to date
        with the rest of your apps.</p>
    </header>
    <section>
      <h2>Add the repository</h2>
      <p>Once, on any distribution with Flatpak. The apps run on Flathub's
        runtimes, which Flatpak fetches from Flathub as they are needed.</p>
      <pre><code>flatpak remote-add --if-not-exists {REMOTE} \\
  {URL}/2c2t.flatpakrepo</code></pre>
      <p>Or open <a href="2c2t.flatpakrepo">2c2t.flatpakrepo</a> with GNOME Software or Discover.</p>
    </section>
    <section>
      <h2>Apps</h2>
{chr(10).join(cards)}
    </section>
    <footer>
      <p>Every app and the repository's summary are signed with the key
        <code>{e(fingerprint)}</code>.</p>
      <p><a href="https://github.com/2c2t-dev/flatpak">How this repository is made</a></p>
    </footer>
  </main>
</body>
</html>
"""


STYLE = """:root {
  --ground: #f6f5f9; --surface: #ffffff; --line: #e1dee9;
  --text: #241f31; --muted: #5e5c64; --accent: #a8307e; --code: #241f31; --code-text: #f6f5f9;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root {
    --ground: #17151c; --surface: #221f29; --line: #34303d;
    --text: #f2f0f6; --muted: #a9a5b3; --accent: #e35db5; --code: #0f0e13; --code-text: #f2f0f6;
    color-scheme: dark;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--ground); color: var(--text);
  font: 16px/1.6 system-ui, -apple-system, "Segoe UI", sans-serif;
}
main {
  max-width: 760px; margin: 0 auto; padding: 48px 16px;
  display: grid; grid-template-columns: minmax(0, 1fr); gap: 40px;
}
h1 { font-size: 2.2rem; line-height: 1.2; margin: 0 0 8px; text-wrap: balance; }
h2 { font-size: 1.3rem; margin: 0 0 12px; }
h3 { font-size: 1.15rem; margin: 0; }
p { margin: 0 0 12px; }
.lead { color: var(--muted); font-size: 1.1rem; }
a { color: var(--accent); }
pre {
  margin: 0 0 12px; padding: 12px 14px; overflow-x: auto;
  background: var(--code); color: var(--code-text); border-radius: 10px;
}
code { font: 0.9rem/1.5 ui-monospace, "JetBrains Mono", monospace; }
.app {
  display: grid; grid-template-columns: 64px minmax(0, 1fr); gap: 20px;
  padding: 20px; background: var(--surface); border: 1px solid var(--line); border-radius: 14px;
}
.app + .app { margin-top: 16px; }
.app img { max-width: 100%; }
.version { color: var(--muted); font-weight: 400; font-size: 0.95rem; }
.about p:first-of-type { color: var(--muted); }
.links { display: flex; gap: 16px; align-items: center; margin: 0; }
.button {
  background: var(--accent); color: #fff; text-decoration: none; font-weight: 600;
  padding: 6px 16px; border-radius: 999px;
}
footer { color: var(--muted); font-size: 0.9rem; border-top: 1px solid var(--line); padding-top: 20px; }
footer code { overflow-wrap: anywhere; }
@media (max-width: 480px) { .app { grid-template-columns: minmax(0, 1fr); } }
"""


def site(out: Path, key: Path, fingerprint: str, versions: dict) -> None:
    listed = apps()
    key64 = base64.b64encode(key.read_bytes()).decode()
    (out / "icons").mkdir(parents=True, exist_ok=True)
    for app in listed:
        with urllib.request.urlopen(app["icon"], timeout=30) as icon:
            (out / "icons" / f"{app['id']}.svg").write_bytes(icon.read())
        (out / f"{app['id']}.flatpakref").write_text(flatpakref(app, key64))
    # The repository's own icon is the first app's, until 2c2t has one.
    (out / "icon.svg").write_bytes((out / "icons" / f"{listed[0]['id']}.svg").read_bytes())
    (out / "2c2t.flatpakrepo").write_text(flatpakrepo(key64))
    (out / "index.html").write_text(page(listed, versions, fingerprint))
    (out / "style.css").write_text(STYLE)
    (out / "_headers").write_text(headers(listed))
    (out / "versions.json").write_text(json.dumps(versions, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("versions")
    making = commands.add_parser("site")
    making.add_argument("out", type=Path)
    making.add_argument("--key", type=Path, required=True)
    making.add_argument("--fingerprint", required=True)
    making.add_argument("--versions", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "versions":
        versions = {app["id"]: latest_release(app["repository"]) for app in apps()}
        json.dump(versions, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    else:
        site(args.out, args.key, args.fingerprint, json.loads(args.versions.read_text()))


if __name__ == "__main__":
    main()
