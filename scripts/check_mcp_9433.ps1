$ErrorActionPreference = 'Continue'

try {
  Add-Type -AssemblyName System.Net.Http
} catch {
}

$handler = New-Object System.Net.Http.HttpClientHandler
$handler.UseProxy = $false
$client = New-Object System.Net.Http.HttpClient($handler)
$client.Timeout = [TimeSpan]::FromSeconds(2)

$urls = @(
  'http://127.0.0.1:9433/sse',
  'http://127.0.0.1:9433/mcp',
  'http://127.0.0.1:9433/streamable',
  'http://127.0.0.1:9433/mcp/sse',
  'http://127.0.0.1:9433/'
)

foreach ($u in $urls) {
  try {
    $resp = $client.GetAsync($u).GetAwaiter().GetResult()
    Write-Output ($u + ' -> ' + [int]$resp.StatusCode)
  }
  catch {
    Write-Output ($u + ' -> ERROR: ' + $_.Exception.Message)
  }
}

if ($null -ne $client) {
  $client.Dispose()
}
