pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'coronainfo')
gnome = import('gnome')

gnome.compile_resources(
  'coronainfo',
  'coronainfo.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'coronainfo.in',
  output: 'coronainfo',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

coronainfo_sources = [
  '__init__.py',
  'app.py',
]

install_subdir('utils', install_dir: moduledir)
install_subdir('models', install_dir: moduledir)
install_subdir('views', install_dir: moduledir)
install_subdir('controllers', install_dir: moduledir)
install_data(coronainfo_sources, install_dir: moduledir)
