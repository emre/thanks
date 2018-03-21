from setuptools import setup

setup(
    name='witness_thanks',
    version='0.0.1',
    packages=["thanks",],
    url='http://github.com/emre/thanks',
    license='MIT',
    author='emre yilmaz',
    author_email='mail@emreyilmaz.me',
    description='A thanks bot for STEEM witnesses to thank their voters after their vote',
    entry_points={
        'console_scripts': [
            'thanks = thanks.tx_listener:main',
        ],
    },
    install_requires=["steem_dshot", "emoji"]
)