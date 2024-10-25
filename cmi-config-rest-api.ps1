<#

Nach was soll gesucht werden können?
- namefull           mandant/nameFull
- nameshort          mandant/nameShort
- installid          mandant/installId
- dbname             mandant/[prod or test]/db/name
- applizenzserver    mandant/[prod or test]/app/lizenzserver
- owinmandant        mandant/[prod or test]/owinServer_relay/mandant

zusätzlich Filter für prod/test

Was für Felder von mandant sollen zurückgegeben werden?
- namefull                mandant/nameFull
- nameshort               mandant/nameShort
- installid               mandant/installId
- dbserver                mandant/[prod or test]/db/server
- dbname                  mandant/[prod or test]/db/name
- appserver               mandant/[prod or test]/app/server
- appinstallpathroot      mandant/[prod or test]/app/installPathRoot
- appuser                 mandant/[prod or test]/app/user
- applizenzserver         mandant/[prod or test]/app/lizenzserver




caddy for reverse proxy:
- download and install caddy
- caddy.exe run ---> create windows service
- caddyfile:
:80 {
    reverse_proxy /api/data localhost:8081
}
- caddy.exe reload


endpoint example:
http://your-server-ip/api/data?nameFull=Bedarfmanagement&server=ziaxiomapsql02

#>





# Define the listener URL and port
$listenerUrl = "http://localhost:8081/"
# path to XML file
$xmlFilePath = "C:\DBA-Scripts\CMI-Config-API\cmi-mandanten-config.xml"






# Start HTTP Listener
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($listenerUrl)
$listener.Start()
Write-Host "Listening on $listenerUrl"




# Function to apply filters based on query parameters
function Filter-XmlData {
    param ($xmlData, $filters)
			write-host "filters: $filters"

    # Filter for <mandant> elements based on the provided filters
    $filteredMandants = $xmlData.mandanten.mandant | Where-Object {
        $matches = $true
        foreach ($filterKey in $filters.Keys) {
			write-host "filterkey: $filterKey"
            # Access nested attributes based on filter keys
            $nodeValue = $_ | Select-Xml -XPath "*[name()='$filterKey']" | ForEach-Object { $_.Node.InnerText }
            if ($nodeValue -notmatch [regex]::Escape($filters[$filterKey])) {
                $matches = $false
                break
            }
        }
        $matches
    }
    return $filteredMandants
}


function ConvertFrom-Xml {
  param([parameter(Mandatory, ValueFromPipeline)] [System.Xml.XmlNode] $node)
  process {
    if ($node.DocumentElement) { $node = $node.DocumentElement }
    $oht = [ordered] @{}
    $name = $node.Name
	write-host $name
    if ($node.FirstChild -is [system.xml.xmltext]) {
      $oht.$name = $node.FirstChild.InnerText
    } else {
      $oht.$name = New-Object System.Collections.ArrayList 
	  
      foreach ($child in $node.ChildNodes) {
        $null = $oht.$name.Add((ConvertFrom-Xml $child))
      }
    }
	write-host $oht.$name
    $oht
  }
}


# Handle incoming requests
while ($listener.IsListening) {
    $context = $listener.GetContext()
    $response = $context.Response
    $request = $context.Request

    # Ensure only GET requests are handled
    if ($request.HttpMethod -eq "GET" -and $request.Url.AbsolutePath -eq "/api/data") {
        # Load XML data
        $xmlData = [xml](Get-Content -Path $xmlFilePath)

        # Get query parameters for filtering
        $filters = @{}
        foreach ($key in $request.QueryString.AllKeys) {
            $filters[$key] = $request.QueryString[$key]
        }

        # Apply filters to XML data
        $filteredData = Filter-XmlData -xmlData $xmlData -filters $filters
		$jsonResponse = $filteredData | ConvertFrom-Xml | ConvertTo-Json -Depth 10

        # Write JSON response
        $buffer = [System.Text.Encoding]::UTF8.GetBytes($jsonResponse)
        $response.ContentType = "application/json"
        $response.ContentLength64 = $buffer.Length
        $response.OutputStream.Write($buffer, 0, $buffer.Length)
    } else {
        # Handle non-GET requests or unknown paths
        $response.StatusCode = 404
        $buffer = [System.Text.Encoding]::UTF8.GetBytes("Endpoint Not Found")
        $response.ContentLength64 = $buffer.Length
        $response.OutputStream.Write($buffer, 0, $buffer.Length)
    }

    # Close the response
    $response.Close()
}

# Stop listener if done
$listener.Stop()
