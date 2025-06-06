using UnityEngine;
using UnityEditor;
using System.IO;
using System.Collections.Generic;
using Unity.Plastic.Newtonsoft.Json.Linq;

public class FbxMetadataPostprocessor : AssetPostprocessor
{
    void OnPostprocessModel(GameObject importedObject)
    {
        string fbxPath = assetPath;
        string jsonPath = Path.ChangeExtension(fbxPath, ".json");

        if (!File.Exists(jsonPath)) return;

        string jsonText = File.ReadAllText(jsonPath);
        JObject root = JObject.Parse(jsonText);

        var meta = importedObject.AddComponent<CustomFbxMetadata>();
        meta.metadata = new List<ObjectProperty>();

        foreach (var obj in root)
        {
            string objName = obj.Key;
            JObject props = (JObject)obj.Value;

            var objectProp = new ObjectProperty
            {
                objectName = objName,
                properties = new List<KeyValue>()
            };

            foreach (var kv in props)
            {
                objectProp.properties.Add(new KeyValue
                {
                    key = kv.Key,
                    value = kv.Value.ToString()
                });
            }

            meta.metadata.Add(objectProp);
        }

        Debug.Log($"[FBX Metadata] Loaded metadata for {importedObject.name} from {jsonPath}");
    }
}
