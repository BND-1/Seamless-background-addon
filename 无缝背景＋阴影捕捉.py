bl_info = {
    "name": "一键无缝背景＋阴影捕捉",
    "author": "杨庭毅",
    "version": (1, 1),
    "blender": (3, 60, 0),
    "location": "属性面板 > 世界",
    "description": "快速添加无缝背景和阴影捕捉功能",
    "category": "Scene",
}

import bpy
import os

def update_background_color(self, context):
    """当颜色改变时更新背景材质"""
    # 查找背景对象
    background_objects = [obj for obj in bpy.data.objects 
                         if any(name in obj.name for name in ["背景", "Background", "Plane"])]
    
    for obj in background_objects:
        if obj.material_slots:
            material = obj.material_slots[0].material
            if material and material.use_nodes:
                # 查找RGB节点
                rgb_node = next((n for n in material.node_tree.nodes 
                                 if n.type == 'RGB'), None)
                if rgb_node:
                    # Update the RGB node color with the new color
                    rgb_node.outputs[0].default_value = self.background_color[:3] + (1.0,)
                else:
                    print(f"No RGB node found in material: {material.name}")

def register_properties():
    bpy.types.Scene.background_color = bpy.props.FloatVectorProperty(
        name="背景颜色",
        subtype='COLOR',
        default=(1.0, 1.0, 0.0, 1.0),  # 初始颜色为黄色
        min=0.0,
        max=1.0,
        size=4,
        update=update_background_color
    )

def unregister_properties():
    del bpy.types.Scene.background_color

class AddSceneOperator(bpy.types.Operator):
    """一键添加无缝背景场景"""
    bl_idname = "scene.add_background_scene"
    bl_label = "添加无缝背景"
    
    def execute(self, context):
        # 获取插件目录路径
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(addon_dir, "background.blend")
        
        try:
            # 首先获取要导入的对象名称
            with bpy.data.libraries.load(filepath) as (data_from, _):
                print("Available objects:", data_from.objects)
                
            # 加载必要的数据
            with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
                # 只导入世界设置和材质
                data_to.worlds = data_from.worlds
                data_to.materials = data_from.materials
                data_to.node_groups = data_from.node_groups
                
                # 过滤对象：包含指定名称但不以"Emission Plane"开头的对象
                background_objects = ["背景", "Background", "Plane"]
                data_to.objects = [name for name in data_from.objects 
                                 if any(obj_name in name for obj_name in background_objects)
                                 and not name.startswith("Emission Plane")]
            
            # 将加载的对象添加到当前场景
            for obj in data_to.objects:
                if obj is not None:
                    if obj.name not in context.scene.objects:
                        context.collection.objects.link(obj)
            
            # 设置世界环境
            if data_to.worlds:
                context.scene.world = data_to.worlds[0]
            
            self.report({'INFO'}, "成功导入无缝背景场景")
            
        except Exception as e:
            self.report({'ERROR'}, f"导入失败: {str(e)}")
            return {'CANCELLED'}
            
        return {'FINISHED'}

class BackgroundScenePanel(bpy.types.Panel):
    """无缝背景场景面板"""
    bl_label = "无缝背景场景"
    bl_idname = "SCENE_PT_background"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
    
    def draw(self, context):
        layout = self.layout
        layout.operator(AddSceneOperator.bl_idname, text="一键添加无缝背景")
        
        # 添加颜色选择器
        layout.prop(context.scene, "background_color", text="背景颜色")

classes = (
    AddSceneOperator,
    BackgroundScenePanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_properties()

def unregister():
    unregister_properties()
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
