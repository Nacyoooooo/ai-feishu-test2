你是一个pytest测试用例生成助手，下面根据以下步骤提取数据并生成满足我要求的代码，回答的内容只需要生成的代码即可，并使用中文回答。
注意！！！！以下是API测试用例的通用生成模板，你必须严格根据提供的json数据生成对应接口的pytest测试用例，场景完全由json数据决定！！！！！！
# 1. 提取json中需要的数据

根据下面的json数据检索出以下内容：请求路径、请求参数、请求体、响应体以及响应体中的不同code，json数据如下：

{{json_data}}

# 2. 测试用例生成规则

请严格按照以下规则生成测试用例：

1. **仅基于JSON数据中的错误码**：只生成JSON数据中明确存在的错误码对应的测试用例
2. **使用提供的测试数据**：如果从上述表格中的数据不能满足你生成需要的场景的测试用例，则不生成这个测试用例，并在最后告诉我
3. **严格按照代码示例格式**：遵循提供的代码结构和命名规范

# 3. 根据代码示例生成代码

代码规范和示例如下，请严格遵守以下几点：

1. 严格按照我给你的代码示例和格式规范
2. 示例代码中调用的函数默认已被实现，不要自己实现
3. 代码中不要有没有意义的注释，如"# 发送消息"、"# 断言"、"# 成功时验证返回数据"之类
4. 函数、类、代码文件等命名根据对应的场景来命名，命名规范同样按照示例代码中命名
5. 有一部分场景测试用例需要额外代码实现或者参数不方便在yaml文件中书写，比如"消息体超长限制"、"超出调用频率限制"等这类用例，你可以单独写一个函数并通过编码实现这个场景来执行这个测试用例，其余参数仍然用一个函数执行
6. 除了第5条中需要单独编写函数来执行的测试用例，其他测试用例的参数都写在yaml文件中，并从yaml文件中读取
7. 如果存在我给你的场景和第5条中都不能够覆盖的错误码，请在生成完代码后告知我这些错误码以及对应的场景
8. 生成的代码必须包括三个文件：api接口、测试用例代码、测试用例参数

```
下面是要生成的代码，我给你介绍一下整个项目的基本逻辑
import requests
from requests.exceptions import RequestException
import urllib.parse
```

```
class APIClient:
    def __init__(self):
        self.base_url = "https://open.feishu.cn"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        })

    def _request(self, method, endpoint, **kwargs):
        """Base request method with error handling"""
        url = self.base_url + endpoint
        response = self.session.request(method, url, **kwargs)
        return response.json()

    def get(self, endpoint, params=None):
        """Send GET request"""
        return self._request('GET', endpoint, params=params)

    def post(self, endpoint, json=None,files=None):
        """Send POST request"""
        return self._request('POST', endpoint, json=json,files=files)

    def put(self, endpoint, json=None):
        """Send PUT request"""
        return self._request('PUT', endpoint, json=json)

    def delete(self, endpoint):
        """Send DELETE request"""
        return self._request('DELETE', endpoint)

    def close(self):
        """Close the session"""
        self.session.close()

def get_app_access_token(app_id, app_secret):
    # 完整API地址
    url = 'https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal'

    # 请求体数据
    payload = {
        'app_id': app_id,
        'app_secret': app_secret
    }

    # 请求头
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # 发送POST请求
    response = requests.post(url, json=payload, headers=headers)

    return response.json()['app_access_token']

if __name__=='__main__':
    from test_data import read_data_from_yaml
    conf=read_data_from_yaml('message_case.yaml', 'robot')
    print(get_app_access_token(conf['app_id'], conf['app_secret']))
```

这是基础的api

```通用API调用模板
from api.base_api import APIClient
import json

class {{API_NAME}}API(APIClient):
    def __init__(self, access_token):
        self.access_token = access_token
        super().__init__()

    def {{api_method}}(self, **kwargs):
        """{{API_DESCRIPTION}}"""
        endpoint = "{{ENDPOINT}}"
        return self.{{HTTP_METHOD}}(endpoint, {{REQUEST_PARAMS}})
```



# 集群

```
import os


from api.message.send_message_api import SendMessageAPI
from api.group.group import GroupAPI
from api.file.upload_file_api import UploadFileAPI
# tag是标签
from .robot_common import get_app_access_token
# 单个接收者
class Receiver:
    def __init__(self,receiver_id,tags:dict[str]={},receiver_id_type="open_id"):
        self.tags=tags
        self.receiver_id=receiver_id
        self.receiver_id_type=receiver_id_type
# 单个机器人
class Robot:
    def __init__(self, app_id, app_secret,tags:dict[str]={}):
        self.tags=tags
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = get_app_access_token(app_id, app_secret)
    
# 集群
class Cluster:
    def __init__(self, robots:list[Robot],receivers:list[Receiver]):
        self.robots = robots
        self.receivers =receivers
    
    def getRobot(self,tags:dict[str],max:int=1)->list[Robot]:
        matching_robots = [
            robot for robot in self.robots
            if all(robot.tags.get(k) == v for k, v in tags.items())
        ]
        if max > 0:
            return matching_robots[:max]
        return matching_robots
    
    def getReceiver(self,tags:dict[str],max:int=1):
        matching_receivers = [
            receiver for receiver in self.receivers
            if all(receiver.tags.get(k) == v for k, v in tags.items())
        ]
        if max > 0:
            return matching_receivers[:max]
        return matching_receivers


```



```
@pytest.fixture

def cluster():

    """创建集群"""

    robotsData = read_data_from_yaml(

    "robots.yaml",

    "robots"

    )

    receiversData = read_data_from_yaml(

    "robots.yaml",

    "receivers"

    )

    robots = []

    for robot in robotsData:

        robot = Robot(app_id=robot['app_id'], app_secret=robot['app_secret'], tags=robot['tags'])

        robots.append(robot)

    receivers = []

    for receiver in receiversData:

        receiver = Receiver(receiver_id=receiver['receiver_id'], tags=receiver['tags'],receiver_id_type=receiver['receiver_id_type'])

        receivers.append(receiver)

    # 创建集群

    cluster = Cluster(robots=robots, receivers=receivers)

    yield cluster

```

```
@pytest.mark.P0

@pytest.mark.usefixtures("cluster")

@pytest.mark.parametrize('test_data', read_data_from_yaml(
    "{{TEST_DATA_FILE}}",
    "{{TEST_DATA_KEY}}"
))

def test_api_endpoint(cluster:Cluster, test_data:dict[str,Any]):

    """测试发送消息"""

    if send_message_data.get('skip',False):

        pytest.skip("skip")

    receivers = cluster.getReceiver(tags=send_message_data['receiverTags'],max=1)

    robots = cluster.getRobot(tags=send_message_data['robotTags'],max=1)

    api_client = {{API_NAME}}API(robots[0].access_token)
resp = api_client.{{api_method}}(**test_data['params'])

    assert resp["code"] == send_message_data["expected_code"], \

        f"和预期结果不对应，预期结果：{send_message_data['expected_code']}，实际结果：{resp['code']}"

```



```
对应的测试数据是

robots.yaml

robots:

  - app_id: "cli_a8ee0c6a92e7501c"

    app_secret: "9kbasiKxCyonOjJ2BCfXHcaKLKPA4fJT"

    tags:

      name: "1"

      desc: "全功能"

      owner: chenzhihao

  - app_id: "cli_a8e0f7e7cbfb1013"

    app_secret: "0TGhLpe3L1wq1OGfnqwTddGH1IOEhxsH"

    tags:

      name: "czh2"

      desc: "无权限，但有机器人能力"

      owner: chenzhihao

  - app_id: "cli_a8e0f325fae5100d"

    app_secret: "kB0DWoplOTY0lkODgs7ICbPS1VdIYMCY"

    tags:

      name: "czh3"

      desc: "未开启机器人能力"

      owner: chenzhihao

  - app_id: "cli_a8e15047e47c900e"

    app_secret: "nW4zT4mWeHLyYDExLBsHvfxHjBiVGAyp"

    tags:

      name: "czh4"

      desc: "无机器人能力，也没有权限"

      owner: chenzhihao

  - app_id: "cli_a7bbd1060d10500d"

    app_secret: "L41DXelDb3nlt0Vdx0AmXcqzn16aqoTZ"

    tags:

      name: "wky1"

      desc: "有权限，有机器人能力"

      owner: wankaiyi

receivers:

  - receiver_id: ou_adf4e416e22c12c5d4b40e347315f68c

    tags:

      状态: "在职"

      name: "chenzhihao"

      性质: 人

      机器人1: "可见"

    receiver_id_type: "open_id"

  - receiver_id: ou_c8748ca66d4e17d20a34f12b62a6191d

    tags:

      状态: "在职"

      name: "wankaiyi"

      性质: 人

      机器人1: "不可见"

    receiver_id_type: "open_id"

  - receiver_id: ou_530eb3559e88330989945fa8114edc88

    tags:

      状态: "离职"

      name: "heyunjing"

      性质: 人

    receiver_id_type: "open_id"

  - receiver_id: oc_a9bc91faf86be9ea96d20e16e12fd57e

    tags:

      性质: 群聊

      群名: "历史群1"

    receiver_id_type: "chat_id"

  - receiver_id: "oc_c9314af7583d16ba886cca1a8644daaf"

    tags:

      性质: 群聊

      群名: "话题"

    receiver_id_type: "chat_id"

  - receiver_id: "ou_a727999dd34a7de8c77ab4f86bf709cb"

    tags:

      状态: "在职"

      性质: 人

      name: "liyongsheng"

      机器人1: "可见"

    receiver_id_type: "open_id"

  - receiver_id: "ou_a727999dd34a7de8c77ab4f86bf709cb"

    tags:

      状态: "在职"

      性质: 人

      name: "houyongliang"

      机器人1: "可见"

    receiver_id_type: "open_id"

  - receiver_id: oc_8ef3bb6838aa4aaefe3da8cae0c5fd6c

    tags:

      性质: 群聊

      群名: "禁言"

    receiver_id_type: "chat_id"

```



```
{{API_TEST_CASES}}:
  # 通用测试用例模板
  - params: {{
      "param1": "value1",
      "param2": "value2"
    }}
    expected_code: {{expected_code}}
    robotTags: {{
      "tag1": "value1"
    }}
    receiverTags: {{
      "tag1": "value1"
    }}
    skip: false
```
