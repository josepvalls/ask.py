Function Notify-alexa {
  param(
  [string]$message="This is a sample post", #you can leave this and change at command line
  [int]$expire=86400, #one day in seconds
  [int]$sticky=86400, #one day in seconds
  $msgKey #this is used to key messages so you can update/replace and create new
  )

  $url = "ENTER_YOUR_URL"
  $userid = "ENTER_YOUR_ID_CODE"
  $secret = "ENTER_YOUR_SECRET"

  [string]$ts = [int64](([datetime]::UtcNow)-(get-date "1/1/1970")).TotalSeconds
  [int]$stickyTS = [int]$ts + $sticky
  [int]$expireTS = [int]$ts + $expire
  $hash = Get-StringHash ($ts+":"+$secret)
  $hash = @{
            text= "$message"
            userId= $userid
            timestamp= $ts
            hash= $hash
            source= "api"
            sticky= $stickyTS
            expiry= $expireTS
            key= "$msgKey"
  }
  $headers = @{"contenttype"="application/json; charset=utf-8"}
  $JSON = $hash | ConvertTo-Json
  $postedmessage = Invoke-RestMethod -Uri $url -Method Post -Body $JSON -Headers $headers
  $postedmessage #delete this line if you do not need/want to see results on screen
}
