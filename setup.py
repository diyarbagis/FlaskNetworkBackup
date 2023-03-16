from setuptools import setup, find_packages

setup(
    name='FlaskNetworkBackup',
    version='1.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['Flask', 'netmiko'],
    entry_points={
        'console_scripts': [
            'FlaskNetworkBackup  = FlaskNetworkBackup.NetBackup:main'
        ]
    },
    license='GPLv3',
    author='Diyar Bagis',
    author_email='diyarbagis@gmail.com',
    description='A free open-source Flask app for backup on switches,routers and firewalls.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/diyarbagis/FlaskNetworkBackup',
    keywords='flask network firewall switch router backup',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: System :: Networking :: Firewalls',
    ],
)
