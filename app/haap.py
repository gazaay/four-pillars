import logging
from app import bazi

__name__ = "haap"

# Configure logging settings
logging.basicConfig(level=logging.debug,  # Set the minimum level for displayed logs
                    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of log messages
                    filename='app.log',  # File to write logs to
                    filemode='w')  # File mode ('w' for write)

# Create a logger
logger = logging.getLogger(__name__)


# 地支相刑						
# 寅刑巳，巳刑申，申刑寅，為無恩之刑。						
# 未刑丑，丑刑戌，戌刑未，為持勢之刑。						
# 子刑卯，卯刑子，為無禮之刑。						
# 辰刑辰，午刑午，酉刑酉，亥刑亥，為自刑之刑。						
						
# 地支相衝						
# 子午相衝，丑未相衝，寅申相衝，卯酉相衝，辰戌相衝，巳亥相衝。						
						
# 地支相破						
# 子酉相破，午卯相破，巳申相破，寅亥相破，辰丑相破，戌未相破。						
# 地支相害						
# 子未相害，丑午相害，寅巳相害，卯辰相害，申亥相害，酉戌相害。						
						
# 地支六合						
# 子丑合化土	寅亥合化木	卯戌合化火	辰酉合化金	巳申合化水	午未為陰陽中正合化土。	
						
						
# 地支三合						
# 申子辰合成水局	巳酉丑合成金局	寅午戌合成火局	亥卯未合成木局。			

def add_haap_features_to_df(df):
    columns_to_initialize = [
           '本時', '本日', '-本時', '本月', '本年', '-本月', '流時', '流日', '-流時', '流月', '流年', '-流月']
    happ_df = df.copy()

    for index, row in happ_df:
        # 子丑合化土
        if row['本時']： 
            print(row['本時'])