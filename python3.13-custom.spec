%global __brp_mangle_shebangs %{nil}

Name:		python3.13-custom
Version: 	3.13.0
Release: 	1%{?dist}
Summary: 	Custom build of Python 3.13 with Pip included

License: 	Python
URL:		https://www.python.org/
Source0:	https://www.python.org/ftp/python/%{version}/Python-%{version}.tar.xz

BuildRequires:		gcc, make, openssl-devel, bzip2-devel, libffi-devel, zlib-devel

%description
A cleanly compiled version of python3.13 built from source, installed to /opt/python3.13

%prep
# this unzips the tar
%autosetup -n Python-%{version}

%build
#configure the build to dite in /opt, run CPU optimizations, and strictly enforce that PIP is bundled
./configure \
	--prefix=/opt/python3.13 \
	--enable-optimizations \
	--with-ensureip=install

# Compile the code using all availble CPU cores for maximum speed
make %{?_smp_mflags}

%install
#clean out any old build artifacts first
rm -rf ${buildroot}

#install the binaries into the tmp RPM staging area.
#Use 'altinstall' so it doesn't create generic 'python3' symlinks that confuse things
make altinstall DESTDIR=%{buildroot}

%clean
#Clean up the staging area
rm -rf %{buildroot}

%files
#This is the manifest, bundles everything inside
/opt/python3.13/

%changelog
*Thu Jun 4 2026 Quentin H techwith@outlook.com - 3.13.0-1
- Initial RPM relase for pythong with pip
