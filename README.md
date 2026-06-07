#Custom Python 3.13 Build: Debian (.deb) & Red Hat (.rpm)

I needed python 3.13 for my ubuntu laptop, but it wasn't in the apt repos yet. Instead of doing a messy `make install` that could overwrite core OS files and break package managers, 
I turned this into a project to learn how to properly build software from source and package it into a deployable `deb` file. Since I also have a Alma linux server and needed to understand how to deploy an `.rpm` for that environment, 
I decided to tackle both systems back to back.

These packages are built to isolate python entirely inside  `/opt/python3.13`. This prevents any conflicts with the native system's Python on Debian and RHEL based systems.


## Debian Build (.deb)

Building for ubuntu required setting up the `debhelper` toolchain and mapping out a strict `debian/` directory.

### Dev Environment & Build Steps
1. **Toolchain:** Installed `build-essential`, `devscripts`, `debhelper`, and Python's required C-libraries (like `libssl-dev`, `zlib1g-dev`, etc.)
2. **Workspace:** Unpacked the raw Python 3.13 .tar.xz source.
3. **The Debian Directory:** Created `debian/` directory and built the required blueprints:
  - control: Mapped package metadata and dependencies
  - rules: Acted as the core Makefile, utilizing --enable-optimizations for CPU profiling
  - changelog: Set the strict package versioning.
  - compat: Set the Debian Standards version.
4. **Compilation:** Executed the build using `dpkg-buildpackage -us -uc -b`.

### Roadblocks and Troubleshooting
* **The Ghost package:** Initially, `debhelper` packaged an empty `.deb` file; the code compiled sucessfully, but becuase I was using a custom `/op/` prefix, the packager didn't know to use that path. I resolved this by creating a `.install` file to explicitly create `/opt/python3.13`
* **Headless GUI Failures:** Python's substantial test suite runs automatically after the compilation; the Tkinter (TK) test kept crashing due to me building in a terminal, leaving no method for TK to test the GUI. I bypassed this by routing the tests through a virtual framebuffer, `xvfb-run`.
<details>
<summary><b>View Build Error</b></summary>

```text
Failed (failures=1)
test_tkinter failed
dh_auto_test: error:make -j8 test...returned exit code 2
```
</details>

* **Fakeroot failures:** Debian zips packages inside a fakeroot environment, which aritficially broke Python's core OS permissions tests (test_os, test_subprocess, test_posix).
Because the `--enable-optimizations` flag utilizes Profile-Guided Optimization (PGO), Python had already run its entire rigorous test suite during the compilation phase to generate its performance profile. Letting dh_auto_test run afterward simply repeated those tests in a broken environment. I bypassed this redundancy by implementing an override_dh_auto_test directive in the rules file.


<details>
<summary><b>View Build Error</b></summary>

```text
3 tests failed again:
  test_os test_posix test_subprocess
dpkg-buildpackage: error: fakeroot debian/rules binary subprocess returned exit
status 2
```
</details>

## Red Hat Build (.rpm)

Creaing a rpm means using a `.spec` file versus the `./debian` directory that `.deb` packages use.

### Dev Environment & Build steps
1. **Toolchain:** Installed the Red Hat "Developement Tools" group, alongside `rpm-build` and `rpmdevtools`.
2. **Workspace:** Generated the strict RPM directory tree using `rpmdev-setuptree` and placed the raw source tarball directly into the `SOURCES` directory.
3. **`.spec` File:** Wrote a single blueprint in `SPECS/` to handle the `%prep`, `%build`, and `%install` phases. Passed `--with-ensureip=install` to bundle pip

### Roadblocks and troubleshooting
* **Shebang Mangler** Red Hat runs a strict post-build script (`brp-mangle-shebang`) that forcefully rewrites generic python shebangs to python 2 or 3, to prevent version conflicts. Becuase this build is purposefully isolated to `/opt` I elected to disbale the mangler by adding `%global __brp_mangle_shebangs %{nil}` to the top of the `.spec` file, preserving the upstream source code.
<details>
<summary><b>View Build Error</b></summary>

```text
*** ERROR: ambigious python shebang in /opt/python3.13/lib/python3.13/encodings/rot)13.py: #!/usr/bin/env python. Change it to python3 (or python2) explicitly.
error: Bad exit status from /var/tmp/rpm-tmp.mh12Fd (%install)
```
</detail>


