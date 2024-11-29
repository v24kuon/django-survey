/**
 * アンケート管理画面の動的制御
 *
 * 質問タイプの変更を監視し、選択式の場合のみ選択肢を表示します。
 * 非選択式の場合は選択肢を非表示にし、入力値をクリアします。
 */

class SurveyFormController {
    constructor() {
        this.CHOICE_TYPES = ['radio', 'checkbox', 'select'];
        this.initializeEventListeners();
        this.initializeChoicesStyle();
    }

    /**
     * イベントリスナーの初期化
     */
    initializeEventListeners() {
        // 親要素にイベントリスナーを設定（イベント委譲）
        document.addEventListener('change', (event) => {
            const target = event.target;
            if (target.matches('select[name*="question_type"]')) {
                this.handleQuestionTypeChange(event);
            }
        });

        // django-nested-adminのイベントを監視
        document.addEventListener('djnesting:initialized', () => {
            this.updateAllChoicesVisibility();
        });

        document.addEventListener('djnesting:mutate', () => {
            this.updateAllChoicesVisibility();
            this.initializeChoicesStyle();
        });

        // 初期表示時の設定
        this.updateAllChoicesVisibility();
    }

    /**
     * 選択肢グループの初期スタイルを設定
     */
    initializeChoicesStyle() {
        const choicesGroups = document.querySelectorAll('[id$="-choices-group"]');
        choicesGroups.forEach(group => {
            group.style.display = 'none';
        });
    }

    /**
     * すべての質問の選択肢の表示/非表示を更新
     */
    updateAllChoicesVisibility() {
        const selects = document.querySelectorAll('select[name*="question_type"]');
        selects.forEach(select => {
            this.toggleChoicesVisibility(select);
        });
    }

    /**
     * 選択肢の入力値をクリア
     * @param {string} questionId - 質問ID
     */
    clearChoiceInputs(questionId) {
        const choiceInputs = document.querySelectorAll(`input[name^="questions-${questionId}-choices-"][name$="-text"]`);
        choiceInputs.forEach(input => {
            input.value = '';
        });
    }

    /**
     * 質問タイプ変更時の処理
     * @param {Event} event - 変更イベント
     */
    handleQuestionTypeChange(event) {
        const select = event.target;
        this.toggleChoicesVisibility(select);
    }

    /**
     * 選択肢の表示/非表示を切り替え
     * @param {HTMLSelectElement} select - 質問タイプのセレクト要素
     */
    toggleChoicesVisibility(select) {
        const questionId = select.name.match(/questions-(\d+)-question_type/)?.[1];
        if (!questionId) return;

        const choicesGroup = document.getElementById(`questions-${questionId}-choices-group`);
        if (!choicesGroup) return;

        if (this.CHOICE_TYPES.includes(select.value)) {
            choicesGroup.style.display = 'block';
        } else {
            choicesGroup.style.display = 'none';
            this.clearChoiceInputs(questionId);
        }
    }
}

// インスタンス化
document.addEventListener('DOMContentLoaded', () => {
    new SurveyFormController();
});
