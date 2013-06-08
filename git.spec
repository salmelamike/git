# Pass --without docs to rpmbuild if you don't want the documentation
%define _without_docs 0

Name: 		git
Version: 1.8.3
Release: 2
Summary:  	Core git tools
License: 	GPLv2
Group: 		Development/Tools
URL: 		http://git-core.googlecode.com/files/
Source:		http://git-core.googlecode.com/files/%{name}-%{version}.tar.gz
Source1:	git.xinetd
Source2:	git.conf.httpd
Patch1:	0001-git-subtree-properly-handle-remote-refs.patch
BuildRequires:	zlib-devel >= 1.2, python, openssl-devel, libcurl-devel, expat-devel, gettext %{!?_without_docs:, xmlto, asciidoc > 6.0.3}
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:	perl-Git = %{version}-%{release}
Requires:	zlib >= 1.2, libcurl, less, openssh-clients, expat, perl(Error), rsync

%description
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

The git rpm installs the core tools with minimal dependencies.  To
install all git packages, including tools for integrating with other
SCMs, install the git-all meta-package.

%package all
Summary:	Meta-package to pull in all git tools
Group:		Development/Tools
Requires:	git = %{version}-%{release}
Requires:	git-email = %{version}-%{release}
Requires:	gitk = %{version}-%{release}
Requires:	git-gui = %{version}-%{release}
Requires:	perl-Git = %{version}-%{release}
Obsoletes:	git <= 1.6.1.3

%description all
Git is a fast, scalable, distributed revision control system with an
unusually rich command set that provides both high-level operations
and full access to internals.

This is a dummy package which brings in all subpackages.

%package daemon
Summary:	Git protocol daemon
Group:		Development/Tools
Requires:	git = %{version}-%{release}
%description daemon
The git dæmon for supporting git:// access to git repositories

%package -n gitweb
Summary:        Simple web interface to git repositories
Group:          Development/Tools
Requires:       git = %{version}-%{release}

%description -n gitweb
Simple web interface to track changes in git repositories



%package email
Summary:        Git tools for sending email
Group:          Development/Tools
Requires:	git = %{version}-%{release}, perl-Git = %{version}-%{release}
Requires:   perl(Net::SMTP::SSL)
%description email
Git tools for sending email.

%package gui
Summary:        Git GUI tool
Group:          Development/Tools
Requires:       git = %{version}-%{release}, tk >= 8.4
%description gui
Git GUI tool.

%package -n gitk
Summary:        Git revision tree visualiser
Group:          Development/Tools
Requires:       git = %{version}-%{release}, tk >= 8.4
%description -n gitk
Git revision tree visualiser.

%package -n perl-Git
Summary:        Perl interface to Git
Group:          Development/Libraries
Requires:       git = %{version}-%{release}, perl(Error)
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
BuildRequires:  perl(Error), perl(ExtUtils::MakeMaker)

%description -n perl-Git
Perl interface to Git.

%package -n emacs-git
Summary:       Git version control system support for Emacs
Group:         Applications/Editors
Requires:      git = %{version}-%{release}, emacs-common

%description -n emacs-git
%{summary}.

%prep
# Adjusting %%setup since git-pkg unpacks to src/
# %%setup -q
%setup -q -n src
%patch1 -p1

%build
make %{_smp_mflags} CFLAGS="$RPM_OPT_FLAGS" \
     ETC_GITCONFIG=/etc/gitconfig \
     gitexecdir=%{_bindir} \
     prefix=%{_prefix} all %{!?_without_docs: doc}

%install
rm -rf $RPM_BUILD_ROOT
make %{_smp_mflags} CFLAGS="$RPM_OPT_FLAGS" DESTDIR=$RPM_BUILD_ROOT \
     prefix=%{_prefix} mandir=%{_mandir} \
     ETC_GITCONFIG=/etc/gitconfig \
     gitexecdir=%{_bindir} \
     INSTALLDIRS=vendor install %{!?_without_docs: install-doc}
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/xinetd.d
install -m 644 %SOURCE1 $RPM_BUILD_ROOT/%{_sysconfdir}/xinetd.d/git
mkdir -p $RPM_BUILD_ROOT/var/www/git
install -m 644 -t $RPM_BUILD_ROOT/var/www/git gitweb/static/*.png gitweb/static/*.css
install -m 755 -t $RPM_BUILD_ROOT/var/www/git gitweb/gitweb.cgi
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf.d
install -m 0644 %SOURCE2 $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf.d/git.conf

find $RPM_BUILD_ROOT -type f -name .packlist -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type f -name '*.bs' -empty -exec rm -f {} ';'
find $RPM_BUILD_ROOT -type f -name perllocal.pod -exec rm -f {} ';'

(find $RPM_BUILD_ROOT%{_bindir} -type f | grep -vE "archimport|svn|cvs|email|gitk|git-gui|git-citooli|git-daemon" | sed -e s@^$RPM_BUILD_ROOT@@)               > bin-man-doc-files
(find $RPM_BUILD_ROOT%{_datadir}/locale -type f | sed -e s@^$RPM_BUILD_ROOT@@ -e 's/$/*/' ) >> bin-man-doc-files
(find $RPM_BUILD_ROOT%{perl_vendorlib} -type f | sed -e s@^$RPM_BUILD_ROOT@@) >> perl-files
%if %{!?_without_docs:1}0
(find $RPM_BUILD_ROOT%{_mandir} $RPM_BUILD_ROOT/Documentation -type f | grep -vE "email|gitk|git-gui|git-citool" | sed -e s@^$RPM_BUILD_ROOT@@ -e 's/$/*/' ) >> bin-man-doc-files
%else
rm -rf $RPM_BUILD_ROOT%{_mandir}
%endif
mkdir -p $RPM_BUILD_ROOT/var/lib/git-daemon

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d
install -m 644 -T contrib/completion/git-completion.bash $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/git

rm -f $RPM_BUILD_ROOT/%{_bindir}/*svn*
rm -f $RPM_BUILD_ROOT/%{_bindir}/*cvs*
rm -f $RPM_BUILD_ROOT/%{_bindir}/git-archimport

%clean

rm -rf $RPM_BUILD_ROOT


%files -f bin-man-doc-files
%defattr(-,root,root)
%{_datadir}/git-core/
%doc README COPYING Documentation/*.txt contrib/hooks
%{!?_without_docs: %doc Documentation/*.html Documentation/docbook-xsl.css}
%{!?_without_docs: %doc Documentation/howto Documentation/technical}
%{_sysconfdir}/bash_completion.d

%files email
%defattr(-,root,root)
%doc Documentation/*email*.txt
%{_bindir}/*email*
%{!?_without_docs: %{_mandir}/man1/*email*.1*}
%{!?_without_docs: %doc Documentation/*email*.html }

%files gui
%defattr(-,root,root)
%{_bindir}/git-gui
%{_bindir}/git-gui--askpass
%{_bindir}/git-citool
%{_datadir}/git-gui/
%{!?_without_docs: %{_mandir}/man1/git-gui.1*}
%{!?_without_docs: %doc Documentation/git-gui.html}
%{!?_without_docs: %{_mandir}/man1/git-citool.1*}
%{!?_without_docs: %doc Documentation/git-citool.html}

%files -n gitk
%defattr(-,root,root)
%doc Documentation/*gitk*.txt
%{_bindir}/*gitk*
%{_datadir}/gitk
%{!?_without_docs: %{_mandir}/man1/*gitk*.1*}
%{!?_without_docs: %doc Documentation/*gitk*.html }

%files -n perl-Git -f perl-files
%defattr(-,root,root)

%files daemon
%defattr(-,root,root)
%{_bindir}/git-daemon
%config(noreplace)%{_sysconfdir}/xinetd.d/git
/var/lib/git-daemon

%files -n gitweb
%defattr(-,root,root)
/var/www/git/
%{_datadir}/gitweb/
%{python_sitelib}/git_remote_helpers
%{python_sitelib}/git_remote_helpers-0.1.0-*.egg-info

%config(noreplace)%{_sysconfdir}/httpd/conf.d/git.conf

%files all

# No files for you!

