################################################################################
#                               _    ____ ___                                  #
#                              / \  / ___|_ _|                                 #
#                             / _ \| |    | |                                  #
#                            / ___ \ |___ | |                                  #
#       __  __       _ _   _/_/  _\_\____|___|___                              #
#      |  \/  |_   _| | |_(_)___(_) |_ ___  |  _ \  ___ _ __ ___   ___         #
#      | |\/| | | | | | __| / __| | __/ _ \ | | | |/ _ \ '_ ` _ \ / _ \        #
#      | |  | | |_| | | |_| \__ \ | ||  __/ | |_| |  __/ | | | | | (_) |       #
#      |_|  |_|\__,_|_|\__|_|___/_|\__\___| |____/ \___|_| |_| |_|\___/        #
#                                                                              #
################################################################################
#                                                                              #
# Copyright (c) 2015 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
#    Licensed under the Apache License, Version 2.0 (the "License"); you may   #
#    not use this file except in compliance with the License. You may obtain   #
#    a copy of the License at                                                  #
#                                                                              #
#         http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                              #
#    Unless required by applicable law or agreed to in writing, software       #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
################################################################################
import os
from acitoolkit.acitoolkit import *

def createTenantConfig(**kwargs):
    """
    Create a tenant with a single EPG and assign it statically to 2 interfaces.
    This is the minimal configuration necessary to enable packet forwarding
    within the ACI fabric.
    """
    # Create the Tenant
    tenant = Tenant('Coke')

    # Create the Application Profile
    app = AppProfile('AP1', tenant)

    # Create provider and consumer EPGs
    prov_epg = EPG('Prov1', app)
    cons_epg = EPG('Cons1', app)

    # Create a Context and BridgeDomain
    context = Context('Ctx1', tenant)
    bd = BridgeDomain('BD1', tenant)
    bd.add_context(context)

    # Place the EPG in the BD
    prov_epg.add_bd(bd)

    # Declare 2 physical interfaces
    if1 = Interface('eth', '1', '101', '1', '15')
    if2 = Interface('eth', '1', '101', '1', '16')

    # Create VLAN 5 on the physical interfaces
    vlan5_on_if1 = L2Interface('vlan5_on_if1', 'vlan', '5')
    vlan5_on_if1.attach(if1)

    vlan5_on_if2 = L2Interface('vlan5_on_if2', 'vlan', '5')
    vlan5_on_if2.attach(if2)

    # Attach the EPG to the VLANs
    prov_epg.attach(vlan5_on_if1)
    prov_epg.attach(vlan5_on_if2)
    cons_epg.attach(vlan5_on_if1)
    cons_epg.attach(vlan5_on_if2)

    # Create a contract
    contract = Contract('K1', tenant)
    entry1 = FilterEntry('entry1',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='3306',
                         dToPort='3306',
                         etherT='ip',
                         prot='tcp',
                         sFromPort='1',
                         sToPort='65535',
                         tcpRules='unspecified',
                         parent=contract)

    # Provide the contract from 1 EPG and consume from the other
    prov_epg.provide(contract)
    cons_epg.consume(contract)

    # Get the APIC login credentials
    description = 'acitoolkit tutorial application'
    os.environ['APIC_LOGIN'] = kwargs['login']
    os.environ['APIC_PASSWORD'] = kwargs['password']
    os.environ['APIC_URL'] = kwargs['url']
    
    creds = Credentials('apic', description)
    creds.add_argument('--delete', action='store_true',
                       help='Delete the configuration from the APIC')
    args = creds.get()

    # Delete the configuration if desired
    if args.delete:
        tenant.mark_as_deleted()

    # Login to APIC and push the config
    session = Session(args.url, args.login, args.password)
    session.login()
    resp = tenant.push_to_apic(session)
    if resp.ok:
        print 'Success'

    # Print what was sent
    print 'Pushed the following JSON to the APIC %s' % kwargs['url']
    print 'URL:', tenant.get_url()
    print 'JSON:', tenant.get_json()

if __name__ == "__main__":
    apicBaseUrl = 'http://samohan-bld.insieme.local:'
    # Create config on APIC1
    createTenantConfig(login='admin', password='ins3965!', url=apicBaseUrl + '8100')
    # Create config on APIC2
    createTenantConfig(login='admin', password='ins3965!', url=apicBaseUrl + '8200')
