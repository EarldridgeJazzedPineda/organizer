pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'organizer')
gnome = import('gnome')

gnome.compile_resources('organizer',
  'organizer.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python3 = import('python')

conf = configuration_data()
conf.set('PYTHON', python3.find_installation().full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'organizer.in',
  output: 'organizer',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

organizer_sources = [
  '__init__.py',
  'main.py',
  'window.py',
]

install_data(organizer_sources, install_dir: moduledir)
