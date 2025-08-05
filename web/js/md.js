'use strict';

import { startFetch } from './api.js';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

(function () {
    startFetch(`md/strategy.md`).then((data) => {
        if (data) {
            const strategyElement = document.getElementById('strategy');
            strategyElement.innerHTML = DOMPurify.sanitize(marked.parse(data));
            strategyElement.classList.add('nunito-normal');
            strategyElement.querySelector('table').classList.add('table', 'table-bordered', 'table-striped', 'table-hover');
        }
    }).catch((error) => {
        console.error('Error fetching strategy markdown:', error);
    });
})();
