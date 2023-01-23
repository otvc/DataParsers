import json

def ComparingDicts(d1, d2, result = []):
    for key, value in d1.items():
        if isinstance(value, dict):
            ComparingDicts(value, d2[key], result)
        elif isinstance(value, list):
            ComparingLists(value, d2[key], result = result)
        elif isinstance(value, str):
            v1 = value.replace(" ", "")
            v2 = d2[key].replace(" ", "")
            result.append(v1 == v2)
        else:
            result.append(value == d2[key])
    return result

def ComparingLists(l1, l2, result = []):
    for i1, i2 in zip(l1, l2):
        if isinstance(i1, dict):
            ComparingDicts(i1, i2, result=result)
        elif isinstance(i1, list):
            ComparingLists(i1, i2, result=result)
        else:
            result.append(i1==i2)
    return result

def gt_and_doc(path_gt, path_doc, e1='utf-8', e2 = 'utf-8'):
    with open(path_gt,  'r', encoding=e1) as f:
        ground_truth = f.readlines()
        ground_truth = [line.strip() for line in ground_truth]

    with open(path_doc, 'r', encoding=e2) as f:
        doc = f.read()
    
    return ground_truth, doc

def get_gt_dirty_json(path_gt, path_dirty):
    with open(path_gt,  'r') as f:
        gt_json = json.load(f)

    with open(path_dirty, 'r') as f:
        dirty_json = json.load(f)
    
    return gt_json, dirty_json