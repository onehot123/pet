import pandas as pd
from app import app, db, DogBreed
import logging
import traceback

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def import_from_excel(file_path):
    """从Excel文件导入数据到数据库"""
    try:
        # 读取Excel文件
        logger.info(f"开始读取Excel文件: {file_path}")
        df = pd.read_excel(file_path)
        
        # 验证必要的列是否存在
        required_columns = ['中文名', '别名', '原产地', '体重', '身高', '尾部特征', '眼睛特征', '耳朵特征', '毛色', '功能']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Excel文件缺少必要的列: {', '.join(missing_columns)}")
        
        # 导入数据到数据库
        success_count = 0
        update_count = 0
        
        with app.app_context():
            for _, row in df.iterrows():
                # 使用中文名作为breed_id，转换为拼音或英文标识符
                chinese_name = str(row['中文名']).strip()
                breed_id = chinese_name.lower().replace(' ', '_')  # 这里可以添加中文转拼音的功能
                
                # 检查是否已存在
                existing_breed = DogBreed.query.filter_by(breed_id=breed_id).first()
                if existing_breed:
                    # 更新现有记录
                    existing_breed.chinese_name = chinese_name
                    existing_breed.alias = str(row['别名'])
                    existing_breed.origin = str(row['原产地'])
                    existing_breed.weight = str(row['体重'])
                    existing_breed.height = str(row['身高'])
                    existing_breed.tail_feature = str(row['尾部特征'])
                    existing_breed.eye_feature = str(row['眼睛特征'])
                    existing_breed.ear_feature = str(row['耳朵特征'])
                    existing_breed.coat_color = str(row['毛色'])
                    existing_breed.function = str(row['功能'])
                    update_count += 1
                else:
                    # 创建新记录
                    new_breed = DogBreed(
                        breed_id=breed_id,
                        chinese_name=chinese_name,
                        alias=str(row['别名']),
                        origin=str(row['原产地']),
                        weight=str(row['体重']),
                        height=str(row['身高']),
                        tail_feature=str(row['尾部特征']),
                        eye_feature=str(row['眼睛特征']),
                        ear_feature=str(row['耳朵特征']),
                        coat_color=str(row['毛色']),
                        function=str(row['功能']),
                        image=f"{breed_id}.jpg"  # 默认图片名称
                    )
                    db.session.add(new_breed)
                    success_count += 1
            
            db.session.commit()
            logger.info(f"数据导入完成！新增: {success_count} 条, 更新: {update_count} 条")
            return True
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"导入失败: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 2:
        print("使用方法: python import_data.py <Excel文件路径>")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    if import_from_excel(excel_file):
        print("数据导入成功！")
    else:
        print("数据导入失败，请查看日志了解详情。")
        sys.exit(1) 