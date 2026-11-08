param([int]$BrowserProcessId=32872,[ValidateSet('Library','Favorites','Favourites','Spaces','All','Images','')][string]$InvokeName='',[switch]$NavigateFavorites,[ValidateSet('All','Images','Favorites','')][string]$NavigateCollection='',[switch]$ObserveMainWindow)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName Accessibility
$sunnyAccessibilityAssembly=[Accessibility.IAccessible].Assembly.Location
Add-Type -ReferencedAssemblies $sunnyAccessibilityAssembly -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
using Accessibility;
public class SunnyAccessibleObservation {
  public string path,name,name_preview,role,default_action;public int depth,left,top,width,height,children,state;public bool name_clipped,state_read_error,default_action_read_error;
}
public class SunnyAccessibleMetadata {
  public int visited,returned_nodes,child_batches,node_limit=800,depth_limit=20,children_per_node_limit=200;
  public bool node_limit_hit,depth_limit_hit,child_limit_hit;
  public bool folder_completeness_established=false;
  public List<string> errors=new List<string>();
}
public static class SunnyTypedLegacyObserver {
  public static SunnyAccessibleMetadata LastObservation;
  [DllImport("oleacc.dll")]
  public static extern int AccessibleObjectFromWindow(IntPtr hwnd,int objectId,ref Guid iid,[MarshalAs(UnmanagedType.Interface)]out IAccessible accessible);
  [DllImport("oleacc.dll")]
  public static extern int AccessibleChildren([MarshalAs(UnmanagedType.Interface)] IAccessible container,int start,int count,[Out,MarshalAs(UnmanagedType.LPArray,SizeParamIndex=2)]object[] children,out int obtained);
  public delegate bool EnumProc(IntPtr hwnd,IntPtr param);
  [DllImport("user32.dll")]public static extern bool EnumChildWindows(IntPtr parent,EnumProc callback,IntPtr param);
  [DllImport("user32.dll")]public static extern bool IsWindowVisible(IntPtr hwnd);
  [DllImport("user32.dll")]public static extern bool SetForegroundWindow(IntPtr hwnd);
  [DllImport("user32.dll",CharSet=CharSet.Unicode)]public static extern int GetClassName(IntPtr hwnd,StringBuilder name,int length);
  public static List<IntPtr> Renderers(IntPtr parent){var found=new List<IntPtr>();EnumChildWindows(parent,(h,p)=>{var name=new StringBuilder(256);GetClassName(h,name,256);if(IsWindowVisible(h)&&name.ToString()=="Chrome_RenderWidgetHostHWND")found.Add(h);return found.Count<8;},IntPtr.Zero);return found;}
  private class Node { public IAccessible a;public int child,depth;public string path; }
  private static void EnqueueObservedChildren(Node node,int count,Queue<Node> queue,SunnyAccessibleMetadata metadata) {
    if(node.child!=0||count<=0)return;
    if(node.depth>=metadata.depth_limit){metadata.depth_limit_hit=true;return;}
    int limit=Math.Min(count,metadata.children_per_node_limit);
    if(count>limit)metadata.child_limit_hit=true;
    for(int start=0;start<limit;){
      int requested=Math.Min(64,limit-start),obtained=0;
      var children=new object[requested];int result;
      try { result=AccessibleChildren(node.a,start,requested,children,out obtained);metadata.child_batches++; }
      catch(COMException error){metadata.errors.Add(node.path+":children:"+error.ErrorCode);return;}
      if(result<0){metadata.errors.Add(node.path+":children:hresult="+result);return;}
      if(obtained<0||obtained>requested){metadata.errors.Add(node.path+":children:invalid-obtained-count");return;}
      if(obtained==0){if(start<count)metadata.errors.Add(node.path+":children:enumeration-ended-before-reported-count");return;}
      for(int index=0;index<obtained;index++){
        object child=children[index];var accessible=child as IAccessible;
        if(accessible!=null)queue.Enqueue(new Node{a=accessible,child=0,depth=node.depth+1,path=node.path+"/index:"+(start+index)});
        else if(child is int)queue.Enqueue(new Node{a=node.a,child=(int)child,depth=node.depth+1,path=node.path+"/child:"+(int)child});
        else metadata.errors.Add(node.path+":children:unsupported-variant-at-index="+(start+index));
      }
      start+=obtained;
    }
  }
  public static List<SunnyAccessibleObservation> Observe(long handle) {
    var metadata=new SunnyAccessibleMetadata();LastObservation=metadata;
    var iid=new Guid("618736e0-3c3d-11cf-810c-00aa00389b71");IAccessible root;
    int result=AccessibleObjectFromWindow(new IntPtr(handle),-4,ref iid,out root);
    if(result!=0||root==null)throw new InvalidOperationException("No accessible window object.");
    return ReadTree(new Node{a=root,child=0,depth=0,path="0"},metadata);
  }
  private static List<SunnyAccessibleObservation> ReadTree(Node root,SunnyAccessibleMetadata metadata) {
    var queue=new Queue<Node>();queue.Enqueue(root);
    var output=new List<SunnyAccessibleObservation>();
    while(queue.Count>0&&metadata.visited<metadata.node_limit){var node=queue.Dequeue();metadata.visited++;try{
      string name=node.a.get_accName(node.child)??"";string role=Convert.ToString(node.a.get_accRole(node.child));int count=node.child==0?node.a.accChildCount:0;
      int state=-1;string defaultAction=null;bool stateError=false,actionError=false;
      try { state=Convert.ToInt32(node.a.get_accState(node.child)); } catch(COMException error){stateError=true;metadata.errors.Add(node.path+":state:"+error.ErrorCode);}
      try { defaultAction=node.a.get_accDefaultAction(node.child); } catch(COMException error){actionError=true;metadata.errors.Add(node.path+":default-action:"+error.ErrorCode);}
      int left,top,width,height;node.a.accLocation(out left,out top,out width,out height,node.child);
      if(name.Length>0)output.Add(new SunnyAccessibleObservation{path=node.path,name=name,name_preview=name.Length>180?name.Substring(0,180):name,name_clipped=false,role=role,state=state,default_action=defaultAction,state_read_error=stateError,default_action_read_error=actionError,depth=node.depth,left=left,top=top,width=width,height=height,children=count});
      EnqueueObservedChildren(node,count,queue,metadata);
    }catch(COMException error){metadata.errors.Add(node.path+":observation:"+error.ErrorCode);}}
    metadata.node_limit_hit=queue.Count>0;metadata.returned_nodes=output.Count;
    return output;
  }
  public static List<SunnyAccessibleObservation> ObserveLibraryFiles(long handle) {
    var metadata=new SunnyAccessibleMetadata();LastObservation=metadata;
    var iid=new Guid("618736e0-3c3d-11cf-810c-00aa00389b71");IAccessible root;
    int result=AccessibleObjectFromWindow(new IntPtr(handle),-4,ref iid,out root);
    if(result!=0||root==null)throw new InvalidOperationException("No accessible window object.");
    var queue=new Queue<Node>();queue.Enqueue(new Node{a=root,child=0,depth=0,path="0"});
    int visited=0;
    while(queue.Count>0&&visited++<800){var node=queue.Dequeue();try{
      string name=node.a.get_accName(node.child)??"";int role=Convert.ToInt32(node.a.get_accRole(node.child));
      if(name=="Library files"&&role==24){
        var scoped=new SunnyAccessibleMetadata{node_limit=4000,depth_limit=18};LastObservation=scoped;
        return ReadTree(new Node{a=node.a,child=node.child,depth=0,path=node.path},scoped);
      }
      EnqueueObservedChildren(node,node.child==0?node.a.accChildCount:0,queue,metadata);
    }catch(COMException error){metadata.errors.Add(node.path+":find-library-files:"+error.ErrorCode);}}
    metadata.node_limit_hit=queue.Count>0;metadata.errors.Add("Library files container not observed; no collection absence claim.");
    return new List<SunnyAccessibleObservation>();
  }
  public static string InvokeNavigation(long handle,string expectedName) {
    if(expectedName!="Library"&&expectedName!="Favorites"&&expectedName!="Favourites"&&expectedName!="Spaces"&&expectedName!="All"&&expectedName!="Images")throw new InvalidOperationException("Navigation name is not allowed.");
    var iid=new Guid("618736e0-3c3d-11cf-810c-00aa00389b71");IAccessible root;
    int result=AccessibleObjectFromWindow(new IntPtr(handle),-4,ref iid,out root);
    if(result!=0||root==null)throw new InvalidOperationException("No accessible window object.");
    var queue=new Queue<Node>();queue.Enqueue(new Node{a=root,child=0,depth=0,path="0"});
    Node candidate=null;int matches=0,visited=0;
    while(queue.Count>0&&visited++<800){var node=queue.Dequeue();try{
      string name=node.a.get_accName(node.child)??"";int role=Convert.ToInt32(node.a.get_accRole(node.child));int state=Convert.ToInt32(node.a.get_accState(node.child));
      if(name==expectedName&&(role==43||role==30||role==57||role==37)&&(state&0x18000)==0){matches++;candidate=node;}
      if(node.depth<20&&node.child==0){for(int i=1;i<=Math.Min(node.a.accChildCount,200);i++){object child=node.a.get_accChild(i);var accessible=child as IAccessible;queue.Enqueue(new Node{a=accessible??node.a,child=accessible!=null?0:i,depth=node.depth+1,path=node.path+"/"+i});}}
    }catch(COMException){}}
    if(matches!=1)throw new InvalidOperationException("Expected one current visible navigation control; found "+matches);
    candidate.a.accDoDefaultAction(candidate.child);
    return "Invoked visible navigation "+expectedName+" at "+candidate.path;
  }
  public static string Describe(long handle) {
    var iid=new Guid("618736e0-3c3d-11cf-810c-00aa00389b71");
    IAccessible accessible;
    int result=AccessibleObjectFromWindow(new IntPtr(handle),-4,ref iid,out accessible);
    if(result!=0||accessible==null)return "hresult="+result;
    try { return "name="+accessible.get_accName(0)+";children="+accessible.accChildCount; }
    finally { Marshal.ReleaseComObject(accessible); }
  }
}
'@
$sunnyBrowser=Get-Process -Id $BrowserProcessId -ErrorAction Stop
if($sunnyBrowser.ProcessName -notin @('chrome','ChatGPT')){throw 'The requested process is not the inspected browser application.'}
if($ObserveMainWindow){
    $sunnyControls=[SunnyTypedLegacyObserver]::Observe($sunnyBrowser.MainWindowHandle.ToInt64())
    [ordered]@{process_id=$sunnyBrowser.Id;main_window=$sunnyBrowser.MainWindowHandle.ToInt64();description=[SunnyTypedLegacyObserver]::Describe($sunnyBrowser.MainWindowHandle.ToInt64());controls=$sunnyControls;coverage=[SunnyTypedLegacyObserver]::LastObservation}|ConvertTo-Json -Depth 6
    return
}
if($NavigateFavorites -or $NavigateCollection){
    [void][SunnyTypedLegacyObserver]::SetForegroundWindow($sunnyBrowser.MainWindowHandle)
    $sunnyNavigationLog=@()
    $sunnyCollection=if($NavigateCollection){$NavigateCollection}else{'Favorites'}
    foreach($sunnyTarget in @('Library',$sunnyCollection)){
        $sunnyInvoked=$false
        foreach($sunnyHandle in @([SunnyTypedLegacyObserver]::Renderers($sunnyBrowser.MainWindowHandle))){
            $sunnyMatches=@([SunnyTypedLegacyObserver]::Observe($sunnyHandle.ToInt64())|Where-Object {$_.name -ceq $sunnyTarget -and $_.role -in @('43','30','57','37')})
            if($sunnyMatches.Count){
                $sunnyNavigationLog += [SunnyTypedLegacyObserver]::InvokeNavigation($sunnyHandle.ToInt64(),$sunnyTarget)
                $sunnyInvoked=$true
                break
            }
        }
        if(-not $sunnyInvoked){throw ('Navigation target not observed: '+$sunnyTarget)}
        Start-Sleep -Milliseconds 900
    }
    $sunnySnapshots=@()
    foreach($sunnySample in 1..3){
        $sunnyFrames=@()
        foreach($sunnyHandle in @([SunnyTypedLegacyObserver]::Renderers($sunnyBrowser.MainWindowHandle))){
            $sunnyLibraryControls=[SunnyTypedLegacyObserver]::ObserveLibraryFiles($sunnyHandle.ToInt64())
            $sunnyLibraryCoverage=[SunnyTypedLegacyObserver]::LastObservation
            $sunnyControls=[SunnyTypedLegacyObserver]::Observe($sunnyHandle.ToInt64())
            $sunnyFrames += [ordered]@{handle=$sunnyHandle.ToInt64();description=[SunnyTypedLegacyObserver]::Describe($sunnyHandle.ToInt64());controls=$sunnyControls;coverage=[SunnyTypedLegacyObserver]::LastObservation;library_controls=$sunnyLibraryControls;library_coverage=$sunnyLibraryCoverage}
        }
        $sunnySnapshots += [ordered]@{sample=$sunnySample;observed_utc=[DateTime]::UtcNow.ToString('o');windows=$sunnyFrames}
        if($sunnySample -lt 3){Start-Sleep -Milliseconds 900}
    }
    [ordered]@{navigation=$sunnyNavigationLog;snapshots=$sunnySnapshots}|ConvertTo-Json -Depth 7
    return
}
$sunnyResults=@()
foreach($sunnyHandle in @([SunnyTypedLegacyObserver]::Renderers($sunnyBrowser.MainWindowHandle))) {
    if($InvokeName){
        $sunnyNames=@([SunnyTypedLegacyObserver]::Observe($sunnyHandle.ToInt64())|Where-Object {$_.name -ceq $InvokeName -and $_.role -in @('43','30','57','37')})
        if($sunnyNames.Count){[SunnyTypedLegacyObserver]::InvokeNavigation($sunnyHandle.ToInt64(),$InvokeName);return}
        continue
    }
    try {
        $sunnyControls=[SunnyTypedLegacyObserver]::Observe($sunnyHandle.ToInt64())
        $sunnyResults += [ordered]@{handle=$sunnyHandle.ToInt64();description=[SunnyTypedLegacyObserver]::Describe($sunnyHandle.ToInt64());controls=$sunnyControls;coverage=[SunnyTypedLegacyObserver]::LastObservation}
    }
    catch { $sunnyResults += [ordered]@{handle=$sunnyHandle;error=$_.Exception.Message} }
}
if($InvokeName){throw 'The requested navigation control is not currently observed.'}
$sunnyResults | ConvertTo-Json -Depth 4
