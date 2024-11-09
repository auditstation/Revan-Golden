#    Author:(<https://www.warlocktechnologies.com/>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#test
###################################################################################
{
    'name': 'Revan Golden Website',
    'version': '1.0',
    'category': 'website',
    'summary': '',
    'description': '''Revan Golden Website
    ''',
    'author': 'Warlock Technologies Pvt Ltd.',
    'website': 'http://warlocktechnologies.com',
    'support': 'mailto:support@warlocktechnologies.com',
    'depends': ['website','base','website_sale','portal','website_custom_code','website_sale_wishlist'],
    'data': [
        "views/homepage.xml",
        "views/portal_my_home.xml",
        "views/contactus.xml",
        "views/website_product.xml",
        "views/website_sale.xml",
    ],
    'assets': {
    },
    
    'images': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1',
    'external_dependencies': {
    },
}

