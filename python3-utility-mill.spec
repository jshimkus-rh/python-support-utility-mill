%global modname utility-mill

%define repo_name python-support-utility-mill
%define repo_branch main

%define version 1.1.0
%define unmangled_version 1.1.0
%define release 1

Name: python3-%{modname}
Version: %{version}
Release: %{release}
Summary: python3-%{modname}
License: BSD
URL:     https://github.com/dm-vdo/%{repo_name}
Source0: %{url}/archive/refs/heads/%{repo_branch}.tar.gz

BuildArch: noarch

Group: Development/Libraries

# Build requirements.
%if 0%{?rhel} && 0%{?rhel} < 9
BuildRequires: python39
BuildRequires: python39-devel
BuildRequires: python39-rpm-macros
BuildRequires: python39-setuptools
BuildRequires: python39-six
BuildRequires: python39-pyyaml
%else
BuildRequires: python3
BuildRequires: python3-devel
BuildRequires: python3-eventlet
BuildRequires: python3-py
BuildRequires: python3-rpm-macros
BuildRequires: python3-setuptools
BuildRequires: python3-six
BuildRequires: python3-pyyaml
%endif

# Runtime requirements.
%if 0%{?rhel} && 0%{?rhel} < 9
Requires: python39
Requires: python39-pyyaml
%else
Requires: python3
Requires: python3-pyyaml
%endif

%?python_enable_dependency_generator

%description
UNKNOWN

%prep
%autosetup -n %{repo_name}-%{repo_branch}

%build
%py3_build

%install
%py3_install

%files -n python3-%{modname}
%{python3_sitelib}/mill/
%{python3_sitelib}/python3_utility_mill-%{version}*

%changelog
* Wed Thu 18 2024 Joe Shimkus <jshimkus@redhat.com> - 1.1.0-1
- Support environmental overrides for defaults.

* Wed Jul 19 2023 Joe Shimkus <jshimkus@redhat.com> - 1.0.7-3
- Changed build setup per template.

* Fri Apr 28 2023 Joe Shimkus <jshimkus@redhat.com> - 1.0.7-2
- Extract defaults file format and access as standalone data file;
  defaults becomes a subclass.

* Thu Apr 20 2023 Joe Shimkus <jshimkus@redhat.com> - 1.0.7-1
- When retrieving a defaults intermediate dictionary from the user defaults
  get the same from the system defaults and return a copy of that updated
  from the user defaults.  This provides the totality, at the requested level,
  of defaults in the dictionary.

* Mon Feb 20 2023 Joe Shimkus <jshimkus@redhat.com> - 1.0.6-2
- Log defaults lookup attempt from user defaults file.
  This avoids confusion as to whether the user defaults are queried.

* Mon Oct 24 2022 Joe Shimkus <jshimkus@redhat.com> - 1.0.6-1
- Changed package generation per Red Hat example.

* Tue Jul 26 2022 Joe Shimkus <jshimkus@redhat.com> - 1.0.5-1
- Make functional rpm for RHEL earlier than 9.0.
- Sync version with setup.py.
