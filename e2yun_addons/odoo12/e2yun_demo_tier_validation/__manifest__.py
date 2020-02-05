# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "E2yun Demo Tier Validation",
    "summary": "Extends the functionality of Demo to "
               "support a tier validation process.",
    "version": "12.0.1.0.0",
    "category": "Agreement",
     'website': 'http://e2yun.cn',
    "author": "chuqiu",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "agreement",
        "agreement_legal",
        "base_tier_validation",
    ],
    "data": [
        "views/base_tier_validation_view.xml",
        "views/agreement_view.xml",
    ],
}