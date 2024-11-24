project('organizer',         version: '0.1.0',
  meson_version: '>= 0.55.0',
)

i18n = import('i18n')

dependency('libhandy-1')

subdir('data')
subdir('src')
subdir('po')

meson.add_install_script('build-aux/meson/postinstall.py')
