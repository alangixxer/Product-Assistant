
### 5. Create an Amazon API

Now that our Lambda function has been created and is working. There needs to be an API Gateway integration set up so Lambda can have a path to Twilio.

From API Gateway's Console and your choice of region (it doesn't need to match the Lambda function's region), select 'Create API':

<details>
<summary><strong>Step-by-step instructions (expand for details)</strong></summary><p>

1. From the AWS Management Console, choose **Services** then select **API Gateway**.


![](IMAGES/api-1.png)


2. Create a new API. The API in this example is the name is **ProductAssistantAPI**.


![](IMAGES/api-2.png)

4. In **Actions** click on **Create Resource**.

<img src="IMAGES/api-3.png" alt="drawing" width="500px"/>

5. Enter a **Resource Name** and the **Resource Path** will be autofilled as the same.  Leave Configure as proxy resource and Enable API Gateway CORS as blank. Click **Create Resource**.


![](IMAGES/api-4.png)


6. Click on the newly created resouce and click on **Actions**.  Select **Create Method**.


<img src="IMAGES/api-5.png" alt="drawing" width="500px"/>



7. Select **Post** and click the **check mark**.  For integration type, select **Lambda Function**.  **Use Lambda Proxy integration** should be left unchecked.  The **Region** must be the same as the Product_Assistant Lambda function created earlier.  Select **Product_Assistant** as the **Lambda Function**.  Keep **Use Default Timeout**.  Hit save and accept the warning after it pops up.


![](IMAGES/api-6.png)


8. Select the newly created **Post** and then click on **Integration Request**.  

![](IMAGES/api-7.png)

9. Once opened, click on **Mapping Templates** at the bottom.  Change **Request body passthrough** to **When there are no templates defined (recommended)**.  Click on the ***plus symbole*** to **Add mapping template**.  Add **application/x-www-form-urlencoded**.  Click the check mark next to the inserted content.  Below, a content box will appear. 

<img src="IMAGES/api-8.png" alt="drawing" width="500px"/>

10. Insert the below **code** into the content box.  This code was suggested by ***https://forums.aws.amazon.com/message.jspa?messageID=675886*** to split our HTTP parameters into JSON key/value pairs.

```
#set($httpPost = $input.path('$').split("&"))
{
#foreach( $kvPair in $httpPost )
 #set($kvTokenised = $kvPair.split("="))
 #if( $kvTokenised.size() > 1 )
   "$kvTokenised[0]" : "$kvTokenised[1]"#if( $foreach.hasNext ),#end
 #else
   "$kvTokenised[0]" : ""#if( $foreach.hasNext ),#end
 #end
#end
}
```

11. Scroll up to the top and click on the blue **Method Execution** link.**Twilio** expects a 200 HTTP status code of type **application/xml**.  Click on the **Integration Response**. Expand the **200** Method Response Status, then expand the 'Body Mapping Templates'.  If there is an 'application/json' entry, remove that now.

![](IMAGES/api-9.png)

12. Click on **add mapping template** and insert **application/xml**. Click the check mark.  Enter the below **code** into the context box. This will allow only the Lambda return fuction to pass through.

```
#set($inputRoot = $input.path('$')) 
$inputRoot
```

13. Click on the **Actions** drop down and select **Deploy API**.  

<img src="IMAGES/api-10.png" alt="drawing" width="200px"/>

14. Select a **New Stage* like **dev**.  Click on **Deploy**.

<img src="IMAGES/api-11.png" alt="drawing" width="500px"/>

15.  Take note of the **Invoke URL**.

![](IMAGES/api-12.png)
 
</p></details>
---

### 6. Set up a Twilio SNS Project.

