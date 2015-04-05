/**
 * Created by sanny on 05.04.15.
 */

document.getElementById('links').onclick = function (event) {
    event = event || window.event;
    var target = event.target || event.srcElement,
        link = target.src ? target.parentNode : target,
        options = {
            index: link, event: event, onslide: function (index, slide) {
                var text = this.list[index].getAttribute('data-description'),
                    node = this.container.find('.description');
                node.empty();
                if (text) {
                    node[index].innerHTML = text;
                }
            }
        },
        links = this.getElementsByTagName('a');
    blueimp.Gallery(links, options);
};