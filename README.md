
### 5. Create an Amazon API

Now that our Lambda function has been created and is working. There needs to be an API Gateway integration set up so Lambda can have a path to Twilio.

From API Gateway's Console and your choice of region (it doesn't need to match the Lambda function's region), select 'Create API':

<details>
<summary><strong>Step-by-step instructions (expand for details)</strong></summary><p>

1. From the AWS Management Console, choose **Services** then select **API Gateway**.


![](IMAGES/api-1.png)


2. Create a new API. The API in this example is the name is **ProductAssistantAPI**.


![](IMAGES/api-2.png)


3. Enter ***table name above*** for the **Table name**. This field is case sensitive.

<img src="IMAGES/api-3.png" alt="drawing" width="200px"/>
![](IMAGES/api-3.png =250x)


4. In **Actions** click on **Create Resource**.


![](IMAGES/api-3.png)


5. Enter a **Resource Name** and the **Resource Path** will be autofilled as the same.  Leave Configure as proxy resource and Enable API Gateway CORS as blank. Click **Create Resource**.


![](IMAGES/api-4.png)


6. Click on the newly created resouce and click on **Actions**.  Select **Create Method**.


![](IMAGES/api-5.png)


7. Select **Post** and click the **check mark**.  For integration type, select **Lambda Function**.  **Use Lambda Proxy integration** should be left unchecked.  The **Region** must be the same as the Product_Assistant Lambda function created earlier.  Select **Product_Assistant** as the **Lambda Function**.  Keep **Use Default Timeout**.  Hit save and accept the warning after it pops up.


![](IMAGES/api-6.png)


<!-- NEED IMAGE FOR THIS -->
    ![Create table screenshot](../images/ddb-create-table.png)

1. Scroll to the bottom of the Overview section of your new table and note the **ARN**. You will use this in the next section.

</p></details>

---

### 6. Set up a Twilio SNS Project.

