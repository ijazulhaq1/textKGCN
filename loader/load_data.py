import gc
from os.path import join
from helper import io_utils as io, file_utils as file
from config import FLAGS
from loader.dataset import TextDataset
from model.build_graph import build_text_graph_dataset
from helper.utils import load, save


def load_data():
    dir = join(io.get_cache_path(), 'split')
    dataset_name = FLAGS.dataset
    train_ratio = int(FLAGS.tvt_ratio[0] * 100)
    val_ratio = int(FLAGS.tvt_ratio[1] * 100)
    test_ratio = 100 - train_ratio - val_ratio
    if 'small' in dataset_name:
        save_fn = '{}_train_{}_val_{}_test_{}_seed_{}_window_size_{}_wikidata_{}'.format(dataset_name, train_ratio,
                                                                                        val_ratio, test_ratio,
                                                                                        FLAGS.random_seed, FLAGS.word_window_size,
                                                                                        FLAGS.use_wikidata)
    else:
        save_fn = '{}_train_val_test_{}_window_size_{}_wikidata_{}'.format(dataset_name, FLAGS.random_seed,
                                                                           FLAGS.word_window_size, FLAGS.use_wikidata)
    path = join(dir, save_fn)
    rtn = load(path)
    if rtn:
        train_data, val_data, test_data = rtn['train_data'], rtn['val_data'], rtn['test_data']
    else:
        train_data, val_data, test_data = _load_tvt_data_helper()
        if FLAGS.use_cache:
            save({'train_data': train_data, 'val_data': val_data, 'test_data': test_data}, path)

    raw_doc_list = file.get_sentences(dataset_name)

    return train_data, val_data, test_data, raw_doc_list


def _load_tvt_data_helper():
    dir = join(io.get_cache_path(), 'all')
    path = join(dir, FLAGS.dataset + '_all_window_' + str(FLAGS.word_window_size) + "_" + str(FLAGS.use_wikidata))
    rtn = load(path)
    if rtn:
        dataset = TextDataset(None, None, None, None, None, None, rtn)
    else:
        dataset = build_text_graph_dataset(FLAGS.dataset, FLAGS.word_window_size)
        gc.collect()
        if FLAGS.use_cache:
            save(dataset.__dict__, path)

    train_dataset, val_dataset, test_dataset = dataset.tvt_split(FLAGS.tvt_ratio[:2], FLAGS.tvt_list, FLAGS.random_seed)
    return train_dataset, val_dataset, test_dataset
