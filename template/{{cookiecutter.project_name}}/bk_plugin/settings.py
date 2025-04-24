import os
from aidev_agent.api.utils import get_endpoint
from aidev_agent.config import settings
from blueapps.patch.settings_paas_services import STATICFILES_DIRS

CUR_DIR = os.path.dirname(__file__)

STATICFILES_DIRS += [os.path.join(CUR_DIR, "dist/static")]


# 网关接口
APIGW_ENDPOINT = get_endpoint(settings.APP_CODE, settings.BK_APIGW_STAGE)
