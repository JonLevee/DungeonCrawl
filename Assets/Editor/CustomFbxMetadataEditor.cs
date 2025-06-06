using UnityEditor;
using UnityEngine;

[CustomEditor(typeof(CustomFbxMetadata))]
public class CustomFbxMetadataEditor : Editor
{
    public override void OnInspectorGUI()
    {
        var metadata = (CustomFbxMetadata)target;

        if (metadata.metadata == null || metadata.metadata.Count == 0)
        {
            EditorGUILayout.HelpBox("No metadata found.", MessageType.Info);
            return;
        }

        foreach (var objProp in metadata.metadata)
        {
            EditorGUILayout.LabelField($"Object: {objProp.objectName}", EditorStyles.boldLabel);

            if (objProp.properties == null || objProp.properties.Count == 0)
            {
                EditorGUILayout.LabelField("  (No properties)");
                continue;
            }

            EditorGUI.indentLevel++;
            foreach (var kv in objProp.properties)
            {
                EditorGUILayout.BeginHorizontal();
                EditorGUILayout.LabelField(kv.key, GUILayout.MaxWidth(150));
                EditorGUILayout.LabelField(kv.value);
                EditorGUILayout.EndHorizontal();
            }
            EditorGUI.indentLevel--;
            EditorGUILayout.Space();
        }
    }
}
