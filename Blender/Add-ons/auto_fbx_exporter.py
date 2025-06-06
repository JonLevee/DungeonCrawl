bl_info = {
    "name": "Auto FBX Exporter for Unity",
    "author": "ChatGPT",
    "version": (1, 7),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > FBX Exporter",
    "description": "Manually export FBX and optional metadata for Unity.",
    "category": "Import-Export",
}

import bpy
import os
import json
from bpy.props import BoolProperty
from bpy.types import Operator

# === Helper Function to Find Root ===
def find_project_root(start_path):
    path = os.path.abspath(start_path)
    while True:
        if os.path.isdir(os.path.join(path, "Assets", "Models")):
            return path
        new_path = os.path.dirname(path)
        if new_path == path:
            return None  # Reached drive root
        path = new_path

# === Logging FBX Export Flags ===
def log_fbx_export_flags():
    print("\n[FBX Export] Valid FBX export flags:")
    op_props = bpy.ops.export_scene.fbx.get_rna_type().properties
    for prop_id, prop in sorted(op_props.items()):
        if prop_id != "rna_type":
            val = prop.default
            desc = prop.description.strip().replace("\n", " ")
            print(f"  {prop_id:<25} {str(val):<15} {desc}")

# === Export Metadata to JSON ===
def export_custom_properties_to_json(filepath):
    metadata = {}
    for obj in bpy.data.objects:
        if obj.keys():
            metadata[obj.name] = {}
            for key in obj.keys():
                if key != '_RNA_UI':
                    metadata[obj.name][key] = obj[key]

    if metadata:
        json_path = os.path.splitext(filepath)[0] + ".json"
        with open(json_path, 'w') as json_file:
            json.dump(metadata, json_file, indent=4)
        print(f"[FBX Export] Exported metadata to: {json_path}")

# === Export Logic ===
def export_fbx_for_unity(context):
    prefs = context.scene.auto_fbx_exporter_settings
    blend_path = bpy.data.filepath
    if not blend_path:
        return None, "Save the .blend file first."

    project_root = find_project_root(blend_path)
    if not project_root:
        return None, "Could not locate project root containing Assets/Models."

    rel_path = os.path.relpath(blend_path, os.path.join(project_root, "Blender"))
    rel_path_no_ext = os.path.splitext(rel_path)[0]
    export_path = os.path.join(project_root, "Assets", "Models", rel_path_no_ext + ".fbx")
    os.makedirs(os.path.dirname(export_path), exist_ok=True)

    hidden_objects = []
    if not prefs.include_shape_keys:
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and obj.data.shape_keys:
                obj.hide_render = True
                hidden_objects.append(obj)

    if prefs.log_flags:
        log_fbx_export_flags()

    try:
        print(f"[FBX Export] Exporting to: {export_path}")

        bpy.ops.export_scene.fbx(
            filepath=export_path,
            use_selection=False,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_ALL',
            object_types={'MESH', 'ARMATURE'} | ({'CAMERA'} if prefs.include_cameras else set()),
            bake_anim=True,
            add_leaf_bones=False,
            use_custom_props=True,
            use_mesh_modifiers=True,
            axis_forward='-Z',
            axis_up='Y'
        )

        if prefs.export_json:
            export_custom_properties_to_json(export_path)

    except Exception as e:
        for obj in hidden_objects:
            obj.hide_render = False
        return None, f"Export failed: {str(e)}"

    for obj in hidden_objects:
        obj.hide_render = False

    print(f"[FBX Export] Export completed.")
    return export_path, None

# === Property Group ===
class AutoFBXExporterSettings(bpy.types.PropertyGroup):
    include_cameras: BoolProperty(
        name="Include Cameras",
        description="Export camera objects along with models and rigs",
        default=False
    )
    include_shape_keys: BoolProperty(
        name="Include Shape Keys",
        description="Include shape key data (e.g. facial expressions or morph targets) in the exported FBX",
        default=True
    )
    log_flags: BoolProperty(
        name="Log All Flags",
        description="Print all available FBX export flags to the system console",
        default=False
    )
    export_json: BoolProperty(
        name="Export Custom Properties as JSON",
        description="Export all custom properties from Blender objects into a sidecar .json file for Unity to read",
        default=True
    )

# === Popup Message Operator ===
class AUTO_FBX_OT_popup_message(Operator):
    bl_idname = "wm.auto_fbx_popup"
    bl_label = "Export Result"

    message: bpy.props.StringProperty()

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=400)

    def draw(self, context):
        layout = self.layout
        for line in self.message.split('\n'):
            layout.label(text=line)

# === Operator for Manual Export ===
class AUTO_FBX_OT_export_button(Operator):
    bl_idname = "export_scene.auto_fbx_export"
    bl_label = "Export FBX for Unity"
    bl_description = "Export this .blend file as an FBX to the Unity project's Assets/Models folder"

    def execute(self, context):
        wm = context.window_manager
        wm.progress_begin(0, 100)
        wm.progress_update(10)

        export_path, error = export_fbx_for_unity(context)

        wm.progress_end()

        if error:
            bpy.ops.wm.auto_fbx_popup('INVOKE_DEFAULT', message=error)
            self.report({'WARNING'}, error)
        else:
            msg = f"Exported to:\n{export_path}"
            bpy.ops.wm.auto_fbx_popup('INVOKE_DEFAULT', message=msg)
            self.report({'INFO'}, msg)

        return {'FINISHED'}

# === UI Panel ===
class AUTO_FBX_PT_panel(bpy.types.Panel):
    bl_label = "FBX Exporter"
    bl_idname = "AUTO_FBX_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FBX Exporter'

    def draw(self, context):
        layout = self.layout
        prefs = context.scene.auto_fbx_exporter_settings

        layout.prop(prefs, "include_cameras")
        layout.prop(prefs, "include_shape_keys")
        layout.prop(prefs, "log_flags")
        layout.prop(prefs, "export_json")
        layout.operator("export_scene.auto_fbx_export", icon='EXPORT')

# === Register/Unregister ===
classes = [
    AutoFBXExporterSettings,
    AUTO_FBX_OT_export_button,
    AUTO_FBX_OT_popup_message,
    AUTO_FBX_PT_panel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.auto_fbx_exporter_settings = bpy.props.PointerProperty(type=AutoFBXExporterSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.auto_fbx_exporter_settings

if __name__ == "__main__":
    register()
