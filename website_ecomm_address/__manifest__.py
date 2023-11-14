# -- coding: utf-8 --
###############################################################################

#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': "Website Ecomm Address",
    'version': '16.0.1.0.0',
    'category': 'Website',
    'summary': """This module helps you to show or hide fields by switching 
    on/off toggles,set fields as mandatory or not and  set default country.""",
    'description': """This module helps you to show or hide fields by switching
    on/off toggles.You can set fields as mandatory or not and also set default
    country.All of these features can be changed from configuration settings 
    of Website  module.""",
    'author': 'OpenCyber',
    'company': 'OpenCyber',
    'maintainer': 'OpenCyber',
    'website': "https://www.opencyber.co",
    'depends': ['base', 'website_sale'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/website_sale_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'website_ecomm_address/static/src/css/'
            'address_management.css',
        ],
    },
    'images': [
        'static/description/banner.jpg',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
