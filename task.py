from flask import Flask, request, jsonify
from nltk.tree import Tree, ParentedTree

app = Flask(__name__)

nps = []

# пошук однорідних NP
def find_parent_np(tree):
    result = []
    parent_np = []
    if tree.label() == 'NP' and any([child for child in tree if child.label() in {',', 'CC'}]):  
        child_nps = []
        for child in tree:
            if child.label() == "NP" and child not in nps:
                child_nps.append(str(child))
        nps.append(child_nps)
        parent_np.append(tree)
    for child in tree:
        if isinstance(child, Tree):
            parent_np.extend(find_parent_np(child))
    return nps

#перестановки
def permute_list(lst):
    if len(lst) == 1:
        return [lst]
    else:
        result = []
        for i in range(len(lst)):
            first_elem = lst[i]
            rest_list = lst[:i] + lst[i+1:]
            for permuted_rest in permute_list(rest_list):
                result.append([first_elem] + permuted_rest)
        return result


def permute_nested_lists(nested_list):
    if len(nested_list) == 1:
        return [[lst] for lst in permute_list(nested_list[0])]
    else:
        first_list = nested_list[0]
        rest_lists = nested_list[1:]
        result = []
        for permuted_first_list in permute_list(first_list):
            for permuted_rest_lists in permute_nested_lists(rest_lists):
                result.append([permuted_first_list] + permuted_rest_lists)
        return result


def replace_last(string, old, new):
    return new.join(string.rsplit(old, 1))


def build_permutation_trees(permutations, str_tree):
    result_permut_trees = []
    for permut_ind in range(len(permutations)):
        str_tree_copy = (str_tree + '.')[:-1]
        #str_tree_permut = ''
        for level_ind in range(len(permutations[permut_ind])):
            for phrase_ind in range(len(permutations[permut_ind][level_ind])):
                old_word = permutations[0][level_ind][phrase_ind]
                new_word = permutations[permut_ind][level_ind][phrase_ind]
                if str_tree_copy.count(old_word) > 1:
                    str_tree_copy = replace_last(str_tree_copy, old_word, new_word)
                else:
                    str_tree_copy = str_tree_copy.replace(old_word, new_word)
        result_permut_trees.append({"tree": str_tree_copy})
    return result_permut_trees


@app.route("/paraphrase")
def get_result():
    tree_str = request.args.get('tree', type=str)
    tree = ParentedTree.fromstring(tree_str)
    str_tree = ' '.join(str(tree).split())
    limit = request.args.get('limit', 20, type=int)
    
    nps_lists = find_parent_np(tree)
    permutations = permute_nested_lists(nps_lists)
    result = build_permutation_trees(permutations, str_tree)

    if len(result) > limit:
        result = result[:limit]
    return { "paraphrases" : result} 



if __name__ == '__main__':
    app.run(debug=True, port=5000)
