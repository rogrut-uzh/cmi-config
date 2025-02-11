# CMI Config

This repository includes information about the CMI configuration of every CMI mandant. The data is saved in the file `static\cmi-config.xml`. 

For accessing the data, this repo also includes a REST API that works with Python 3 and is accessible on `http://localhost:5001/api/data` or [https://zidbacons02.uzh.ch/api/data](https://zidbacons02.uzh.ch/api/data). See "API documentation" for more details at the end of this document.

## Prerequisites
  - install python3 (make available to all windows users)
  - and packages: pip install Flask xmltodict (as administrator so that it's available to all users)
  - The XML file with the CMI configuration must be present and accessible. Modify the path if nescessary.
  - Change api_port in `cmi-config-rest-api.py` if you want to run it on a different port than 5001.

## Windows Service "cmi-config-api"

Created with nssm ([The Non-Sucking Service Manager](https://nssm.cc/)).

  - CMD: `nssm install cmi-config-api`
  - CMD: `nssm edit cmi-config-api`
    - Path: `python.exe`
    - Startup Directory: `D:\gitlab\cmi-config`
    - Arguments: `D:\gitlab\cmi-config\cmi-config-rest-api.py`
  - Logon with Local System account, Startup Automatic.

## XML Structure

```
***** CMI or AIS
<cmi>

    ***** Environment prod or test
    <prod>
    
        ***** Every mandant has its own set of config nodes. 
        <mandant>

        ***** Full Name of the mandant. 
        <namefull>Medizinische Fakultät</namefull>

        ***** Short name of the mandant. 
        <nameshort>MF</nameshort>

        ***** InstallId
        <installid>2624</installid>

        ***** Database information. 
        ***** Excerpt from MetaTool.ini:
        ***** [DataBase]
        ***** Dialect = SQLServer
        ***** ConnectString = Data Source=ZIAXIOMAPSQL02,1433;Initial Catalog=axioma_dfpdib;Trusted_Connection=True;Pooling=true
        <database>

            ***** Host where the database is located
            <host>ZIAXIOMAPSQL02</host>

            __ Database name
            <name>axioma_medizinfak</name>

        </database>

        ***** app specific information
        <app>

            ***** Release version number
            <releaseversion>22.0.10</releaseversion>

            ***** host name where the mandant is installed
            <host id="6ps">ziaxiomapap03</host>

            ***** installation path on host
            <installpath>C:\Program Files\CMI AG\CMI Produktiv\Medizinische Fakultaet 22.0.10</installpath>

            ***** windows service names and users
            <servicename>CMI Medizinische Fakultaet 22.0.10</servicename>
            <serviceuser>UZH\srv_cmi_mef</serviceuser>
            <servicenamerelay>CMIRelayOPCServiceuzhmef</servicenamerelay>
            <serviceuserrelay>Network Service</serviceuserrelay>
        </app>
        
        ***** Server and Port of the licence server that the mandant is using. 
        ***** In case it is missing, the licence is stored directly in mandant app. 
        ***** Excerpt from MetaTool.ini:
        ***** [LicenseServer]
        ***** Port=10325
        ***** Server=ziaxiomatap02
        <licenseserver>
            <port>10325</port>
            <server>ziaxiomatap02</server>
        </licenseserver>

        ***** mobilefirst: Web client URL. 
        ***** Excerpt from MetaTool.ini:
        ***** [MobileFirst]
        ***** Url=https://uzhgstest.cmicloud.ch
        <mobilefirst>https://uzhfpi.cmicloud.ch</mobilefirst>

        ***** STS: CMI Security Token Service. See https://dokumentation.cmiag.ch/cmi-sts-3/latest/
        <sts>

            ***** ea: Enterprise App. Redirects. Verwaltet durch Thomas Schurter.
            <ea>https://sts3.prod.cmicloud.ch/uzhmef/identity/signin-oidc</ea>

            ***** desktopclient: This URL must be provided in the desktop client STS settings.
            <desktopclient>https://sts3.prod.cmicloud.ch/uzhmef</desktopclient>

        </sts>
        
        ***** Objektloader. The app runs on this port. 
        ***** Excerpt from MetaTool.ini:
        ***** [ObjektLoader]
        ***** Port=10245
        ***** Server=ziaxiomatap02
        ***** Im MetaTool.ini von Server steht nur der host z.B. zaixiomapap03
        ***** Im MetaTool.ini von Client steht der FQDN (ohne "d") drin, z.B. ziaxiomapap03.uzh.ch
        <objektloader>
            <port id="6ps">10070</port>
        </objektloader>

        ***** Webconsole. The sub-services use this port. 
        ***** Excerpt from MetaTool.ini:
        ***** [WebConsole]
        ***** Port=10246
        ***** MachineName=ziaxiomapap03
        <webconsole>
            <port ref="6ps">10071</port>
        </webconsole>

        ***** Überweisungen
        <ueberweisung>

            ***** port: The client can be reached via this port. 
            ***** Excerpt from MetaTool.ini:
            ***** [Ueberweisung]
            ***** Port=10247
            ***** MachineName=ziaxiomapap03
            <port ref="1ts">10072</port>

            ***** url: Transfers can be made to the following URLs. They must have the counterpart in their own list. These URLs are maintained in the desktop client. Search for type "Server" will list them (log in as administrator).
            <url ref="1" name="UZH-BM">http://ziaxiomapap03:10112/UeberweisungsService</url>
            <url ref="3" name="UZH-GS">http://ziaxiomapap03:10242/UeberweisungsService</url>
            <url ref="" name="AFI-UR">http://10.74.145.110:28412/UeberweisungsService</url>
        </ueberweisung>

        ***** owinserver: Enables communication from the desktop client and web client. 
        ***** Excerpt from MetaTool.ini:
        ***** [OwinServer]
        ***** Server=*
        ***** PortPrivate=10248
        ***** PortPublic=10249
        ***** Mandant=uzhgstest
        ***** MobileClients_BaseDirectory="C:\Program Files\CMI AG\CMI Test\Generalsekretariat 22.0.10\MobileClients"
        ***** *****
        ***** Excerpt from Thinkecture.Relay.OnPremiseConnectorService.exe.config:
        ***** <relayServer baseUrl="https://relay.cmiaxioma.ch/" ignoreSslErrors="false" timeout="00:00:30">
        *****       <security authenticationType="Identity" accessTokenRefreshWindow="0.00:01:00"> 
        *****           <identity userName="uzhirevtest" password="asgXfO1BP5f+JGc1HvLOiec+Qb/AQD3hnHY2IcsxdIKGajsi3gxfE7cmZV6ejOcPc2a6QO7/7EDhpQADIw3h8sMiMtE17wu/RdJ3BEs7CMCUURx5CH9bkEvNmQLDDSQ35/hrcQ==" />
        *****       </security>
        *****       <onPremiseTargets>
        *****           <web key="webapiprivate" baseUrl="http://ziaxiomatap02:10088/" />
        *****           <web key="webapipublic" baseUrl="http://ziaxiomatap02:10089/" />
        *****       </onPremiseTargets>
        ***** </relayServer>
        ***** *****
        ***** Relay server is always https://relay.cmiaxioma.ch/
        <owinserver>
            <mandant>uzhmef</mandant>
            <port>
                <private ref="6ps">10073</private>
                <public ref="6ps">10074</public>
            </port>
        </owinserver>

        ***** Mügi. Stored in the desktop client.
        <muegi>
            <url fromId="3">http://ziaxiomapap03:10242/MuegiService</url>
            <url fromId="unirat">http://10.74.145.110:28412/MuegiService</url>
        </muegi>

        ***** mobile apps
        ***** they are independent to the webclient. Push service has no effect.
        <mobile>
            <zusammenarbeitdritte>https://mobile.cmiaxioma.ch/zusammenarbeitdritte/uzhgs</zusammenarbeitdritte>
            <sitzungsvorbereitung>https://mobile.cmiaxioma.ch/sitzungsvorbereitung/uzhgs</sitzungsvorbereitung>
            <dossierbrowser>https://mobile.cmiaxioma.ch/dossierbrowser/uzhgs</dossierbrowser>
        </mobile>
        
        ***** Jobs that are defined within desktop client.
        <jobs>
            <adrsync>20:30-MoDiMiDoFrSaSo-weekly</adrsync>
            <fulltextoptimize>21:00-MoDiMiDoFr-weekly</fulltextoptimize>
            <fulltextrebuild>00:05-Sa-weekly</fulltextrebuild>
        </jobs>
```

## API Endpoints

Returns data in JSON. 

### All available data

```
http://localhost:5001/api/data
```

### CMI Apps

```
http://localhost:5001/api/data/cmi
```

### AIS Apps

```
http://localhost:5001/api/data/ais
```

### CMI Apps in PROD environment

```
http://localhost:5001/api/data/cmi/prod
```

### AIS Apps in TEST environment

```
http://localhost:5001/api/data/ais/test
```

### CMI Apps in PROD environment, only 

```
http://localhost:5001/api/data/ais/test
```

### Filtering

`?` followed by the keys and value. Examples:

```
http://localhost:5001/api/data/cmi?app/releaseversion=24.0.6
http://localhost:5001/api/data/cmi/prod?app/releaseversion=22.0.10
http://localhost:5001/api/data?namefull=philo
http://localhost:5001/api/data/cmi/prod?ueberweisung/port=10112
```
