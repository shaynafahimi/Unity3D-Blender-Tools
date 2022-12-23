using UnityEngine;
using UnityEditor;

using System.Collections.Generic;
using System.Collections;
using System.IO;

public class LoadVertMesh : MonoBehaviour
{
    public GameObject go;
    public AnimationClip clip;

    [ContextMenu("Create Curve")]
    void test()
    {
        int num_sh = go.GetComponent<SkinnedMeshRenderer>().sharedMesh.blendShapeCount;
        float time = 0.0f;
        int name = 1;
        float sample = 0.250f;

        for (; name < num_sh; time += sample/2, name++)
        {
            AnimationCurve curve = new AnimationCurve();
            curve.AddKey(time, 000.0f);
            curve.AddKey(time + sample/4, 50.0f);
            curve.AddKey(time + sample/2, 100.0f);
            curve.AddKey(time + sample*3/4, 50.0f);
            curve.AddKey(time + sample, 0.0f);
            AnimationUtility.SetEditorCurve(clip, EditorCurveBinding.FloatCurve("", typeof(SkinnedMeshRenderer), "blendShape.key_"+name.ToString()), curve);



        }



    }
}

public static class MeshSaverEditor {

	[MenuItem("CONTEXT/MeshFiltering/Save Mesh...")]
	public static void SaveMeshInPlace (MenuCommand menuCommand) {
		MeshFilter mf = menuCommand.context as MeshFilter;
		Mesh m = mf.sharedMesh;
		SaveMesh(m, m.name, false, true);
	}

	[MenuItem("CONTEXT/MeshFiltering/Save Mesh As New Instance")]
	public static void SaveMeshNewInstanceItem (MenuCommand menuCommand) {
		MeshFilter mf = menuCommand.context as MeshFilter;
		Mesh m = mf.sharedMesh;
		SaveMesh(m, m.name, true, true);
	}

	public static void SaveMesh (Mesh mesh, string name, bool makeNewInstance, bool optimizeMesh) {
		string path = EditorUtility.SaveFilePanel("Save Mesh Asset", "Assets/", name, "asset");
		if (string.IsNullOrEmpty(path)) return;
        
		path = FileUtil.GetProjectRelativePath(path);

		Mesh meshToSave = (makeNewInstance) ? Object.Instantiate(mesh) as Mesh : mesh;
		
		if (optimizeMesh)
		     MeshUtility.Optimize(meshToSave);
        
		AssetDatabase.CreateAsset(meshToSave, path);
		AssetDatabase.SaveAssets();
	}
	
}